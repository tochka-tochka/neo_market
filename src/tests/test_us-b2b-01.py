import pytest
from django.urls import reverse
from rest_framework import status

from src.tests.fixtures import (
    BaseTestUtil,
    base_data,
    dummy_image,
    product,
    product_factory,
    test_category,
)


@pytest.mark.django_db
class TestCreateProduct(BaseTestUtil):
    def test_create_product_success(self, jwt_client, base_data):
        url = reverse("products")
        response = jwt_client.post(url, base_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED, response.json()
        assert response.json()["status"] == "CREATED"

    def test_seller_id_taken_from_jwt(self, jwt_client, test_user, base_data):
        url = reverse("products")
        response = jwt_client.post(url, base_data, format="json")
        assert response.json()["seller_id"] == str(test_user.id)

    @pytest.mark.parametrize("field_to_remove", ["images", "category"])
    def test_missing_fields_returns_400(self, jwt_client, base_data, field_to_remove):
        del base_data[field_to_remove]
        response = jwt_client.post(reverse("products"), base_data, format="json")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
