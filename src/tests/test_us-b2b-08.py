import pytest
import uuid

from django.urls import reverse
from rest_framework import status
from src.models.product import SKU, ProductStatus, Order, OrderStatus, OrderItem
from src.tests.fixtures import (
    BaseTestUtil,
    base_data,
    dummy_image,
    product,
    product_factory,
    catalog_products,
    sku_payload,
    test_category,
)

@pytest.fixture
def two_skus(product_factory):
    p = product_factory(status=ProductStatus.MODERATED)
    sku1 = SKU.objects.create(product=p, name="SKU 1", price=100, cost_price=80, active_quantity=10, reserved_quantity=0)
    sku2 = SKU.objects.create(product=p, name="SKU 2", price=200, cost_price=80, active_quantity=5, reserved_quantity=0)
    return sku1, sku2

@pytest.fixture
def test_order():
    order = Order.objects.create(status="RESERVED")
    return order

@pytest.mark.django_db
class TestReserveOperations(BaseTestUtil):

    def test_reserve_all_skus_succeeds(self, service_client, two_skus):
        sku1, sku2 = two_skus
        url = reverse("reserve")
        
        payload = {
            "idempotency_key": str(uuid.uuid4()),
            "items": [
                {"sku_id": str(sku1.id), "quantity": 2},
                {"sku_id": str(sku2.id), "quantity": 3}
            ]
        }

        response = service_client.post(url, data=payload, format='json', content_type="application/json")

        assert response.status_code == status.HTTP_200_OK, response.json()
        
        sku1.refresh_from_db()
        sku2.refresh_from_db()
        
        assert sku1.active_quantity == 8
        assert sku1.reserved_quantity == 2
        assert sku2.active_quantity == 2
        assert sku2.reserved_quantity == 3

    def test_partial_insufficient_stock_returns_409_all_rollback(self, service_client, two_skus):
        sku1, sku2 = two_skus
        url = reverse("reserve")
        
        payload = {
            "idempotency_key": str(uuid.uuid4()),
            "items": [
                {"sku_id": str(sku1.id), "quantity": 2},
                {"sku_id": str(sku2.id), "quantity": 10}
            ]
        }

        response = service_client.post(url, data=payload, format='json', content_type="application/json")

        assert response.status_code == status.HTTP_409_CONFLICT, response.json()
        
        sku1.refresh_from_db()
        sku2.refresh_from_db()
        assert sku1.active_quantity == 10
        assert sku2.active_quantity == 5

    def test_idempotent_reserve_returns_200_without_double_deduction(self, service_client, two_skus):
        sku1, _ = two_skus
        url = reverse("reserve")
        key = str(uuid.uuid4())
        
        payload = {
            "idempotency_key": key,
            "items": [{"sku_id": str(sku1.id), "quantity": 1}]
        }

        service_client.post(url, data=payload, format='json', content_type="application/json")
        sku1.refresh_from_db()
        assert sku1.active_quantity == 9

        response = service_client.post(url, data=payload, format='json', content_type="application/json")
        
        assert response.status_code == status.HTTP_200_OK, response.json()
        sku1.refresh_from_db()
        assert sku1.active_quantity == 9

    def test_sku_out_of_stock_event_emitted(self, service_client, two_skus):
        sku1, _ = two_skus
        url = reverse("reserve")
        
        payload = {
            "idempotency_key": str(uuid.uuid4()),
            "items": [{"sku_id": str(sku1.id), "quantity": 10}]
        }

        service_client.post(url, data=payload, format='json', content_type="application/json")
        
        message = self.get_rabbitmq_message('b2c', timeout=2)
        
        assert message is not None
        assert message['event'] == 'SKU_OUT_OF_STOCK'
        assert message['sku_id'] == str(sku1.id)

    def test_unreserve_restores_quantities(self, service_client, two_skus):
        sku1, sku2 = two_skus
        sku1.active_quantity = 5
        sku1.reserved_quantity = 5
        sku1.save()
        order = Order.objects.create(status=OrderStatus.RESERVED)
        OrderItem.objects.create(order=order, sku=sku1, quantity=3)
        url = reverse("unreserve")
        payload = {
            "order_id": order.id,
            "items": [{"sku_id": str(sku1.id), "quantity": 3}]
        }

        response = service_client.post(url, data=payload, format='json', content_type="application/json")
        
        assert response.status_code == status.HTTP_200_OK, response.json()
        
        sku1.refresh_from_db()
        assert sku1.active_quantity == 8
        assert sku1.reserved_quantity == 2