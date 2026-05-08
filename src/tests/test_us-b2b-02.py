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
@pytest.mark.django_db
class TestCreateSKU(BaseTestUtil):

    def test_first_sku_transitions_product_to_moderation(self, jwt_client, test_user, test_category, sku_payload):
        product = Product.objects.create(title="T", category=test_category, seller=test_user, status=ProductStatus.CREATED)
        sku_payload["product_id"] = product.id
        
        response = jwt_client.post(reverse("skus"), sku_payload, format="multipart")
        _ = self.get_rabbitmq_message(queue_name="moder")
        
        product.refresh_from_db()
        assert response.status_code == status.HTTP_201_CREATED
        assert product.status == ProductStatus.ON_MODERATION

    def test_sku_creation_emits_rabbitmq_event(self, jwt_client, test_user, test_category, sku_payload):
        product = Product.objects.create(title="T", category=test_category, seller=test_user, status=ProductStatus.CREATED)
        sku_payload["product_id"] = product.id
        
        jwt_client.post(reverse("skus"), sku_payload, format="multipart")
        
        msg = self.get_rabbitmq_message(queue_name="moder")
        assert msg is not None, msg
        assert msg["product_id"] == str(product.id), msg
        assert "idempotency_key" in msg

    def test_adding_sku_to_moderated_product_keeps_status(self, jwt_client, test_user, test_category, sku_payload):
            product = Product.objects.create(
                title="Approved Product", 
                category=test_category, 
                seller=test_user, 
                status=ProductStatus.MODERATED
            )
            sku_payload["product_id"] = product.id
            
            response = jwt_client.post(reverse("skus"), sku_payload, format="multipart")
            
            product.refresh_from_db()
            assert response.status_code == status.HTTP_201_CREATED
            assert product.status == ProductStatus.MODERATED
            
            msg = self.get_rabbitmq_message(queue_name="moder")
            assert msg is None, "Adding SKU to moderated product should not trigger moderation event"

    def test_cannot_add_sku_to_blocked_product(self, jwt_client, test_user, test_category, sku_payload):
        product = Product.objects.create(title="T", category=test_category, seller=test_user, status=ProductStatus.HARD_BLOCKED)
        sku_payload["product_id"] = product.id
        
        response = jwt_client.post(reverse("skus"), sku_payload, format="multipart")
        assert response.status_code == status.HTTP_403_FORBIDDEN