import uuid

import pytest
from django.urls import reverse
from rest_framework import status

from src.models.product import (
    SKU,
    BlockingReason,
    Product,
    ProductFieldReport,
    ProductStatus,
)
from src.models.user import Seller
from src.tests.fixtures import (
    BaseTestUtil,
    base_data,
    dummy_image,
    product,
    product_factory,
    sku_payload,
    test_category,
)


@pytest.fixture
def blocking_reason():
    r = BlockingReason.objects.create(title="test", comment="test")
    return r


@pytest.fixture
def moderated_product_with_skus(product_factory):
    p = product_factory(title="Product with SKU", status=ProductStatus.MODERATED)
    SKU.objects.create(
        product=p, name="sku1", price=100, cost_price=80
    )
    SKU.objects.create(
        product=p, name="sku2", price=200, cost_price=150
    )
    return p


@pytest.fixture
def blocked_product_with_skus(product_factory, blocking_reason):
    p = product_factory(
        title="Product with SKU",
        status=ProductStatus.BLOCKED,
        blocking_reason_id=blocking_reason.id,
    )
    sku1 = SKU.objects.create(
        product=p, name="sku1", price=100, cost_price=80
    )
    ProductFieldReport.objects.create(product=p, field_name="title", comment="wrong title")
    ProductFieldReport.objects.create(
        product=p, sku=sku1, field_name="images", comment="wrong images"
    )
    return p


@pytest.mark.django_db
class TestCheckStatus(BaseTestUtil):
    def test_get_moderated_product_returns_full_payload(
        self, jwt_client, moderated_product_with_skus, product_factory
    ):
        url = reverse("product-detail", args=[moderated_product_with_skus.id])

        response = jwt_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == ProductStatus.MODERATED
        assert response.json()["blocking_reason"] is None
        for i in range(len(response.json()["skus"])):
            assert response.json()["skus"][i]["cost_price"] is not None

    def test_get_blocked_product_returns_blocking_reason_and_field_reports(
        self, jwt_client, blocked_product_with_skus, product_factory, blocking_reason
    ):
        url = reverse("product-detail", args=[blocked_product_with_skus.id])

        response = jwt_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == ProductStatus.BLOCKED
        assert response.json()["blocking_reason"]["title"] == blocking_reason.title
        assert response.json()["blocking_reason"]["comment"] == blocking_reason.comment
        assert len(response.json()["field_reports"]) > 0

    def test_get_others_product_returns_404(
        self, jwt_client, product_factory, test_category
    ):
        another_user_id = uuid.uuid4()
        another_seller = Seller.objects.create(
            id=another_user_id, username="test_user_2", password="password123"
        )
        other_product = Product.objects.create(
            title="Other", category=test_category, seller=another_seller
        )

        url = reverse("product-detail", args=[other_product.id])

        response = jwt_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_nonexistent_returns_404(self, jwt_client, product_factory):
        url = reverse("product-detail", args=["00000000-0000-0000-0000-000000000000"])

        response = jwt_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
