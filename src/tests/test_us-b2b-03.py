import uuid

import pytest
from django.urls import reverse
from rest_framework import status

from src.models.product import SKU, Product, ProductStatus
from src.models.user import Seller
from src.tests.fixtures import (
    BaseTestUtil,
    base_data,
    dummy_image,
    product,
    product_factory,
    product_with_skus,
    sku_payload,
    test_category,
)


@pytest.mark.django_db
class TestCreateSKU(BaseTestUtil):
    @pytest.mark.parametrize(
        "initial_status", [ProductStatus.MODERATED, ProductStatus.BLOCKED]
    )
    def test_edit_triggers_moderation_event(
        self, jwt_client, test_user, product_factory, base_data, initial_status
    ):
        product = product_factory(status=initial_status)
        url = reverse("product-detail", args=[product.id])

        self._clear_queues()
        response = jwt_client.patch(url, base_data, format="json")

        assert response.status_code == status.HTTP_200_OK, response.json()
        assert response.json()["status"] == ProductStatus.ON_MODERATION

        msg = self.get_rabbitmq_message("moder")
        assert msg and msg["product_id"] == str(product.id)
        assert "idempotency_key" in msg

    def test_edit_hard_blocked_returns_403(
        self, jwt_client, product_factory, base_data
    ):
        product = product_factory(status=ProductStatus.HARD_BLOCKED)
        response = jwt_client.patch(
            reverse("product-detail", args=[product.id]), base_data, format="json"
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_edit_others_product_returns_403(
        self, jwt_client, product_factory, base_data
    ):
        other_seller = Seller.objects.create_user(username="other", password="pass")
        product = product_factory(seller=other_seller)
        response = jwt_client.patch(
            reverse("product-detail", args=[product.id]), base_data, format="json"
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.parametrize(
        "initial_status", [ProductStatus.MODERATED, ProductStatus.BLOCKED]
    )
    def test_edit_sku_triggers_re_moderation(
        self, jwt_client, test_user, test_category, sku_payload, initial_status
    ):
        product = Product.objects.create(
            title="T", category=test_category, seller=test_user, status=initial_status
        )
        sku = SKU.objects.create(
            name="Old", price=10, cost_price=5, product=product
        )

        url = reverse("specific-sku", args=[sku.id])
        sku_payload["product_id"] = product.id
        sku_payload["discount"] = 2000000

        response = jwt_client.patch(url, sku_payload, format="json")

        product.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK, response.json()
        assert product.status == ProductStatus.ON_MODERATION
        assert response.json()["cost_price"] == sku_payload["cost_price"]
        assert response.json()["discount"] == sku_payload["discount"]

    def test_reserves_preserved_after_sku_edit(
        self, jwt_client, test_user, test_category, sku_payload
    ):
        product = Product.objects.create(
            title="T",
            category=test_category,
            seller=test_user,
            status=ProductStatus.MODERATED,
        )
        sku = SKU.objects.create(
            name="Old",
            price=10,
            cost_price=5,
            article="Old",
            reserved_quantity=999,
            product=product,
        )

        url = reverse("specific-sku", args=[sku.id])
        sku_payload["product_id"] = product.id

        response = jwt_client.patch(
            url, sku_payload | {"reserved_quantity": 1000}, format="json"
        )

        sku.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert sku.reserved_quantity == 999

    def test_edit_sku_of_hard_blocked_product_returns_403(
        self, jwt_client, test_user, test_category, sku_payload
    ):
        product = Product.objects.create(
            title="T",
            category=test_category,
            seller=test_user,
            status=ProductStatus.HARD_BLOCKED,
        )
        sku = SKU.objects.create(
            name="S", price=10, cost_price=5, product=product
        )

        url = reverse("specific-sku", args=[sku.id])
        response = jwt_client.patch(url, sku_payload, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_edit_someone_elses_sku_returns_403(
        self, jwt_client, test_user, test_category, sku_payload
    ):
        another_user_id = uuid.uuid4()
        another_seller = Seller.objects.create(
            id=another_user_id, username="test_user_2", password="password123"
        )
        other_product = Product.objects.create(
            title="Other", category=test_category, seller=another_seller
        )
        sku = SKU.objects.create(
            name="S", price=10, cost_price=5, product=other_product
        )

        url = reverse("specific-sku", args=[sku.id])
        response = jwt_client.patch(url, sku_payload, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN
