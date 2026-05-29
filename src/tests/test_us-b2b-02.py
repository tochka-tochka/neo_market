import pytest
from django.urls import reverse
from rest_framework import status
from src.models.product import Category, Product, ProductStatus, SKU

from src.tests.fixtures import (
    BaseTestUtil,
    base_data,
    dummy_image,
    sku_payload,
    product_with_skus,
    product,
    product_factory,
    test_category,
)
@pytest.mark.django_db(transaction=True)
class TestCreateSKU(BaseTestUtil):

    def test_first_sku_transitions_product_to_moderation(self, jwt_client, test_user, test_category, sku_payload):
        product = Product.objects.create(title="T", category=test_category, seller=test_user, status=ProductStatus.CREATED)
        sku_payload["product_id"] = product.id
        
        response = jwt_client.post(reverse("skus"), sku_payload, format="json", content="application/json")
        _ = self.get_rabbitmq_message(queue_name="moder")
        
        product.refresh_from_db()
        assert response.status_code == status.HTTP_201_CREATED, response.json()
        assert product.status == ProductStatus.ON_MODERATION

    def test_sku_creation_emits_rabbitmq_event(self, jwt_client, test_user, test_category, sku_payload):
        product = Product.objects.create(title="T", category=test_category, seller=test_user, status=ProductStatus.CREATED)
        sku_payload["product_id"] = product.id
        
        jwt_client.post(reverse("skus"), sku_payload, format="json")
        
        msg = self.get_rabbitmq_message(queue_name="moder")
        assert msg is not None, msg
        assert msg["product_id"] == str(product.id), msg
        assert msg["event"] == "CREATED", msg
        assert "idempotency_key" in msg

    def test_adding_sku_to_moderated_re_moderates_product(self, jwt_client, test_user, test_category, sku_payload, product_with_skus):
            sku_payload["product_id"] = product_with_skus.id
            
            response = jwt_client.post(reverse("skus"), sku_payload, format="json")
            
            product_with_skus.refresh_from_db()
            assert response.status_code == status.HTTP_201_CREATED, response.json()
            assert product_with_skus.status == ProductStatus.ON_MODERATION
            
            msg = self.get_rabbitmq_message(queue_name="moder")
            assert msg is not None
            assert msg["product_id"] == str(product_with_skus.id), msg
            assert msg["event"] == "EDITED", msg
            assert "idempotency_key" in msg

    def test_cannot_add_sku_to_blocked_product(self, jwt_client, test_user, test_category, sku_payload):
        product = Product.objects.create(title="T", category=test_category, seller=test_user, status=ProductStatus.HARD_BLOCKED)
        sku_payload["product_id"] = product.id
        
        response = jwt_client.post(reverse("skus"), sku_payload, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN