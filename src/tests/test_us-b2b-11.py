import pytest
from django.urls import reverse
from rest_framework import status

from src.models.product import Product, ProductStatus
from src.models.user import Seller
from src.tests.fixtures import product_factory, test_category


@pytest.mark.django_db
class TestSellerProductsView:
    url_name = "products"

    @pytest.fixture
    def another_seller(self, db):
        return Seller.objects.create_user(
            username="another",
            password="password123",
        )

    def test_list_returns_only_own_products(
        self, jwt_client, test_user, product_factory, another_seller, test_category
    ):
        url = reverse(self.url_name)

        own_product_1 = product_factory(
            seller=test_user, title="My Product 1", status=ProductStatus.MODERATED
        )
        own_product_2 = product_factory(
            seller=test_user, title="My Product 2", status=ProductStatus.MODERATED
        )

        other_product = Product.objects.create(
            title="Not My Product",
            description="Not My Product",
            seller=another_seller,
            category=test_category,
            status=ProductStatus.MODERATED,
        )

        response = jwt_client.get(url)
        assert response.status_code == status.HTTP_200_OK, response.json()
        data = response.json()
        items = data.get("items")
        item_ids = [item["id"] for item in items]

        assert str(own_product_1.id) in item_ids, data
        assert str(own_product_2.id) in item_ids, data
        assert str(other_product.id) not in item_ids, data
        assert data["total_count"] == 2

    def test_idor_query_param_seller_id_ignored(
        self, jwt_client, test_user, product_factory, another_seller
    ):
        url = reverse(self.url_name)

        own_product = product_factory(
            seller=test_user, title="My Product", status=ProductStatus.MODERATED
        )

        other_product = product_factory(
            seller=another_seller, title="Other Product", status=ProductStatus.MODERATED
        )

        response = jwt_client.get(f"{url}?seller_id={str(another_seller.id)}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data.get("items")
        item_ids = [item["id"] for item in items]

        assert str(own_product.id) in item_ids
        assert str(other_product.id) not in item_ids
        assert data["total_count"] == 1

    def test_deleted_visible_with_deleted_flag(
        self, jwt_client, test_user, product_factory
    ):
        url = reverse(self.url_name)

        active_product = product_factory(
            seller=test_user, title="Active Product", status=ProductStatus.MODERATED
        )
        deleted_product = product_factory(
            seller=test_user,
            title="Deleted Product",
            status=ProductStatus.MODERATED,
            deleted=True,
        )

        response = jwt_client.get(f"{url}?include_deleted=true")

        assert response.status_code == status.HTTP_200_OK, response.json()
        data = response.json()
        items = data.get("items", [])
        item_ids = [item["id"] for item in items]

        assert str(active_product.id) in item_ids
        assert str(deleted_product.id) in item_ids
        assert data["total_count"] == 2

    def test_status_filter_works_correctly(self, jwt_client, test_user, product_factory):
        url = reverse(self.url_name)

        moderated_product = product_factory(
            seller=test_user, title="Moderated Product", status=ProductStatus.MODERATED
        )
        blocked_product = product_factory(
            seller=test_user, title="Blocked Product", status=ProductStatus.BLOCKED
        )
        created_product = product_factory(
            seller=test_user, title="Created Product", status=ProductStatus.CREATED
        )

        response = jwt_client.get(f"{url}?status={ProductStatus.BLOCKED}")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data.get("items", [])
        item_ids = [item["id"] for item in items]

        assert str(moderated_product.id) not in item_ids
        assert str(blocked_product.id) in item_ids
        assert str(created_product.id) not in item_ids
        assert data["total_count"] == 1

    def test_search_by_title_case_insensitive(
        self, jwt_client, test_user, product_factory
    ):
        url = reverse(self.url_name)

        product_a = product_factory(
            seller=test_user, title="Awesome Gadget", status=ProductStatus.MODERATED
        )
        product_b = product_factory(
            seller=test_user, title="fantastic gadget", status=ProductStatus.MODERATED
        )
        product_c = product_factory(
            seller=test_user, title="Unique Item", status=ProductStatus.MODERATED
        )

        response = jwt_client.get(f"{url}?search=Gadget")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data.get("items", [])
        item_ids = [item["id"] for item in items]

        assert str(product_a.id) in item_ids
        assert str(product_b.id) in item_ids
        assert str(product_c.id) not in item_ids
        assert data["total_count"] == 2

        response = jwt_client.get(f"{url}?search=awesome")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data.get("items", [])
        item_ids = [item["id"] for item in items]
        assert str(product_a.id) in item_ids
        assert str(product_b.id) not in item_ids
        assert data["total_count"] == 1

    def test_search_by_nonexisiting_title_returns_empty_list(
        self, jwt_client, test_user, product_factory
    ):
        url = reverse(self.url_name)

        product_a = product_factory(
            seller=test_user, title="Awesome Gadget", status=ProductStatus.MODERATED
        )
        product_b = product_factory(
            seller=test_user, title="fantastic gadget", status=ProductStatus.MODERATED
        )
        product_c = product_factory(
            seller=test_user, title="Unique Item", status=ProductStatus.MODERATED
        )

        response = jwt_client.get(f"{url}?search=Gadget")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data.get("items", [])
        item_ids = [item["id"] for item in items]

        assert str(product_a.id) in item_ids
        assert str(product_b.id) in item_ids
        assert str(product_c.id) not in item_ids
        assert data["total_count"] == 2

        response = jwt_client.get(f"{url}?search=testtesttest")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        items = data.get("items", [])
        assert len(items) == 0
        assert data["total_count"] == 0

    def test_invalid_pagination_params_return_error(
        self, jwt_client, test_user, product_factory
    ):
        url = reverse(self.url_name)

        product_a = product_factory(
            seller=test_user, title="Awesome Gadget", status=ProductStatus.MODERATED
        )
        product_b = product_factory(
            seller=test_user, title="fantastic gadget", status=ProductStatus.MODERATED
        )
        product_c = product_factory(
            seller=test_user, title="Unique Item", status=ProductStatus.MODERATED
        )

        response = jwt_client.get(f"{url}?search=Gadget&limit=-1&offset=-1")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, (
            response.json()
        )

    def test_pages_pagination_total_count(
        self, jwt_client, test_user, test_category, product_factory
    ):
        url = reverse(self.url_name)

        for i in range(25):
            product_factory(
                seller=test_user, title=f"Product {i}", status=ProductStatus.MODERATED
            )

        response = jwt_client.get(f"{url}?limit=20&offset=20")

        assert response.status_code == status.HTTP_200_OK, response.json()
        assert response.json()["total_count"] == 25, response.json()
        assert len(response.json()["items"]) == 5, response.json()
