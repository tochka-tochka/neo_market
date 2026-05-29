import uuid

import pytest
from django.urls import reverse
from rest_framework import status

from src.models.product import SKU, Product, ProductStatus
from src.models.user import Seller
from src.tests.fixtures import BaseTestUtil, product_factory, test_category


@pytest.mark.django_db
class TestInvoiceCreation(BaseTestUtil):
    url_name = (
        "invoices"
    )

    def test_create_invoice_with_moderated_sku_returns_201(
        self, jwt_client, product_factory, test_user, test_category
    ):
        product_moderated = product_factory(
            seller=test_user, status=ProductStatus.MODERATED, category=test_category
        )
        sku = SKU.objects.create(
            product=product_moderated,
            name="Moderated SKU",
            price=100,
            cost_price=80
        )

        payload = {
            "items": [{"sku_id": str(sku.id), "quantity": 1}],
        }
        url = reverse(self.url_name)
        response = jwt_client.post(url, data=payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["status"] == "CREATED"

    def test_empty_items_returns_400(self, jwt_client):
        payload = {
            "items": [],
        }
        url = reverse(self.url_name)
        response = jwt_client.post(url, data=payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_non_moderated_sku_returns_400(
        self, jwt_client, product_factory, test_user, test_category
    ):
        product_created = product_factory(
            seller=test_user, status=ProductStatus.CREATED, category=test_category
        )
        sku = SKU.objects.create(
            product=product_created,
            name="Non-Moderated SKU",
            price=100,
            cost_price=80
        )

        payload = {
            "items": [{"sku_id": str(sku.id), "quantity": 1}],
        }
        url = reverse(self.url_name)
        response = jwt_client.post(url, data=payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()

    def test_others_sku_returns_403(self, jwt_client, product_factory, test_category):
        another_seller_id = uuid.uuid4()
        another_seller = Seller.objects.create(
            id=another_seller_id, username="another_seller", password="password123"
        )
        product_other_seller = product_factory(
            seller=another_seller,
            status=ProductStatus.MODERATED,
            category=test_category,
        )
        sku_other_seller = SKU.objects.create(
            product=product_other_seller,
            name="Other Seller SKU",
            price=100,
            cost_price=80
        )

        payload = {
            "items": [{"sku_id": str(sku_other_seller.id), "quantity": 1}],
        }
        url = reverse(self.url_name)
        response = jwt_client.post(url, data=payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN, response.json()