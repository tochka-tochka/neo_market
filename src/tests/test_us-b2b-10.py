import uuid

import pytest
from django.urls import reverse
from rest_framework import status

from src.models.product import SKU, Order, OrderItem, OrderStatus, ProductStatus
from src.tests.fixtures import (
    BaseTestUtil,
    base_data,
    catalog_products,
    dummy_image,
    product,
    product_factory,
    sku_payload,
    test_category,
)


@pytest.fixture
def two_skus(product_factory):
    p = product_factory(status=ProductStatus.MODERATED)
    sku1 = SKU.objects.create(
        product=p,
        name="SKU 1",
        price=100,
        cost_price=80,
        stock_quantity=10,
        reserved_quantity=2,
    )
    sku2 = SKU.objects.create(
        product=p,
        name="SKU 2",
        price=200,
        cost_price=80,
        stock_quantity=5,
        reserved_quantity=5,
    )
    return sku1, sku2


@pytest.mark.django_db
class TestfulfillOperations(BaseTestUtil):
    def test_fulfill_decreases_reserved_quantity_and_stock_quantity_unchanged(
        self, service_client, two_skus
    ):
        sku1, _ = two_skus

        reserve_url = reverse("reserve")
        reserve_quantity = 5
        reserve_payload = {
            "idempotency_key": str(uuid.uuid4()),
            "items": [{"sku_id": str(sku1.id), "quantity": reserve_quantity}],
        }
        reserve_response = service_client.post(
            reserve_url,
            data=reserve_payload,
            format="json",
            content_type="application/json",
        )
        assert reserve_response.status_code == status.HTTP_200_OK, (
            reserve_response.json()
        )

        sku1.refresh_from_db()
        initial_reserved_quantity = sku1.reserved_quantity
        initial_active_quantity = sku1.stock_quantity - sku1.reserved_quantity
        assert initial_active_quantity == 3
        assert initial_reserved_quantity == 2 + reserve_quantity

        fulfill_url = reverse("fulfill")
        fulfill_quantity = 3
        fulfill_payload = {
            "order_id": reserve_response.json()["order_id"],
            "items": [{"sku_id": str(sku1.id), "quantity": fulfill_quantity}],
        }

        response = service_client.post(
            fulfill_url,
            data=fulfill_payload,
            format="json",
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_200_OK, response.json()

        sku1.refresh_from_db()

        assert sku1.reserved_quantity == initial_reserved_quantity - fulfill_quantity
        assert sku1.stock_quantity - sku1.reserved_quantity == initial_active_quantity

        assert (
            Order.objects.get(id=reserve_response.json()["order_id"]).status
            == OrderStatus.FULFILLED
        )

    def test_idempotent_fulfill_no_double_deduction(self, service_client, two_skus):
        sku1, _ = two_skus

        reserve_url = reverse("reserve")
        reserve_quantity = 5
        reserve_payload = {
            "idempotency_key": str(uuid.uuid4()),
            "items": [{"sku_id": str(sku1.id), "quantity": reserve_quantity}],
        }
        reserve_response = service_client.post(
            reserve_url,
            data=reserve_payload,
            format="json",
            content_type="application/json",
        )

        sku1.refresh_from_db()
        initial_active_after_reserve = sku1.stock_quantity - sku1.reserved_quantity
        initial_reserved_after_reserve = sku1.reserved_quantity

        fulfill_url = reverse("fulfill")
        fulfill_quantity = 2
        fulfill_payload = {
            "order_id": reserve_response.json()["order_id"],
            "items": [{"sku_id": str(sku1.id), "quantity": fulfill_quantity}],
        }

        first_response = service_client.post(
            fulfill_url,
            data=fulfill_payload,
            format="json",
            content_type="application/json",
        )
        print(reserve_response.json())
        assert first_response.status_code == status.HTTP_200_OK, first_response.json()
        assert (
            Order.objects.get(id=reserve_response.json()["order_id"]).status
            == OrderStatus.FULFILLED
        ), reserve_response.json()

        sku1.refresh_from_db()
        expected_active_quantity = initial_active_after_reserve
        expected_reserved_quantity = initial_reserved_after_reserve - fulfill_quantity

        assert sku1.stock_quantity - sku1.reserved_quantity == expected_active_quantity
        assert sku1.reserved_quantity == expected_reserved_quantity

        second_response = service_client.post(
            fulfill_url,
            data=fulfill_payload,
            format="json",
            content_type="application/json",
        )
        assert second_response.status_code == status.HTTP_200_OK

        sku1.refresh_from_db()

        assert sku1.stock_quantity - sku1.reserved_quantity == expected_active_quantity
        assert sku1.reserved_quantity == expected_reserved_quantity

    def test_fulfill_wrong_payload_returns_409(
        self, service_client, two_skus
    ):
        sku1, _ = two_skus

        reserve_url = reverse("reserve")
        reserve_quantity = 5
        reserve_payload = {
            "idempotency_key": str(uuid.uuid4()),
            "items": [{"sku_id": str(sku1.id), "quantity": reserve_quantity}],
        }
        reserve_response = service_client.post(
            reserve_url,
            data=reserve_payload,
            format="json",
            content_type="application/json",
        )
        assert reserve_response.status_code == status.HTTP_200_OK, (
            reserve_response.json()
        )

        sku1.refresh_from_db()
        initial_reserved_quantity = sku1.reserved_quantity
        initial_active_quantity = sku1.stock_quantity - sku1.reserved_quantity
        assert initial_active_quantity == 3
        assert initial_reserved_quantity == 2 + reserve_quantity

        fulfill_url = reverse("fulfill")
        fulfill_quantity = 100
        fulfill_payload = {
            "order_id": reserve_response.json()["order_id"],
            "items": [{"sku_id": str(sku1.id), "quantity": fulfill_quantity}],
        }

        response = service_client.post(
            fulfill_url,
            data=fulfill_payload,
            format="json",
            content_type="application/json",
        )

        assert response.status_code == status.HTTP_409_CONFLICT, response.json()

        sku1.refresh_from_db()

        assert sku1.reserved_quantity == initial_reserved_quantity

        assert (
            Order.objects.get(id=reserve_response.json()["order_id"]).status
            == OrderStatus.RESERVED
        )
