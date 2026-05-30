import uuid

import pytest
from django.urls import reverse
from rest_framework import status

from src.models.product import SKU, Product, ProductCharacteristics, ProductStatus
from src.models.user import Seller
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


@pytest.mark.django_db
class TestCatalogProducts(BaseTestUtil):
    url_name = "public-products"

    def test_catalog_returns_moderated_in_stock_products(
        self, service_client, catalog_products
    ):
        url = reverse(self.url_name)
        response = service_client.get(url)

        assert response.status_code == status.HTTP_200_OK, response.json()
        data = response.json()

        items = data.get("items", [])
        item_ids = [item["id"] for item in items]

        assert str(catalog_products["visible"].id) in item_ids
        assert str(catalog_products["visible_2"].id) in item_ids

        assert str(catalog_products["out_of_stock"].id) not in item_ids
        assert str(catalog_products["deleted"].id) not in item_ids
        assert str(catalog_products["created"].id) not in item_ids

    def test_catalog_excludes_hard_blocked(self, service_client, catalog_products):
        url = reverse(self.url_name)
        response = service_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        items = response.json().get("items", [])
        item_ids = [item["id"] for item in items]

        assert str(catalog_products["hard_blocked"].id) not in item_ids

    def test_catalog_missing_service_key_returns_401(self, client):
        url = reverse(self.url_name)
        response = client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_catalog_response_has_no_cost_price(self, service_client, catalog_products):
        url = reverse(self.url_name)
        response = service_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        items = response.json().get("items", [])
        assert len(items) > 0, "Каталог не должен быть пустым"

        for item in items:
            assert "cost_price" not in item
            assert "reserved_quantity" not in item
            for sku in item.get("skus", []):
                assert "cost_price" not in sku
                assert "reserved_quantity" not in sku

    def test_batch_ids_returns_visible_subset(self, service_client, catalog_products):
        url = reverse(self.url_name)

        visible_id = str(catalog_products["visible"].id)
        hidden_id = str(catalog_products["deleted"].id)

        response = service_client.get(f"{url}?ids={visible_id},{hidden_id}")

        assert response.status_code == status.HTTP_200_OK
        items = response.json().get("items", [])
        item_ids = [item["id"] for item in items]

        assert len(items) == 1
        assert visible_id in item_ids
        assert hidden_id not in item_ids

    def test_catalog_sort_price_desc(self, service_client, product_factory):
        url = reverse(self.url_name)

        p1 = product_factory(title="Product Cheap", status=ProductStatus.MODERATED)
        SKU.objects.create(
            product=p1,
            name="sku_cheap",
            price=100,
            cost_price=80,
            stock_quantity=10,
            reserved_quantity=2,
        )

        p2 = product_factory(title="Product Expensive", status=ProductStatus.MODERATED)
        SKU.objects.create(
            product=p2,
            name="sku_exp",
            price=500,
            cost_price=400,
            stock_quantity=10,
            reserved_quantity=2,
        )

        p3 = product_factory(title="Product Medium", status=ProductStatus.MODERATED)
        SKU.objects.create(
            product=p3,
            name="sku_med",
            price=300,
            cost_price=200,
            stock_quantity=10,
            reserved_quantity=2,
        )

        response = service_client.get(f"{url}?sort=price_desc")

        assert response.status_code == status.HTTP_200_OK
        items = response.json().get("items", [])

        test_product_ids = [str(p1.id), str(p2.id), str(p3.id)]
        sorted_ids = [item["id"] for item in items if item["id"] in test_product_ids]

        assert sorted_ids == [str(p2.id), str(p3.id), str(p1.id)]

    def test_catalog_filters_by_category(
        self, service_client, product_factory, test_user
    ):
        url = reverse(self.url_name)

        from src.models.product import Category

        cat_b_id = uuid.uuid4()
        cat_b = Category.objects.create(
            id=cat_b_id, name="Another Category", slug="another_category"
        )

        p_in_cat_a = product_factory(
            title="Cat A Product", status=ProductStatus.MODERATED
        )
        SKU.objects.create(
            product=p_in_cat_a,
            name="sku_a",
            price=100,
            cost_price=80,
            stock_quantity=10,
            reserved_quantity=2,
        )

        p_in_cat_b = Product.objects.create(
            title="Approved Product",
            category=cat_b,
            seller=test_user,
            status=ProductStatus.MODERATED,
        )
        SKU.objects.create(
            product=p_in_cat_b,
            name="sku_b",
            price=100,
            cost_price=80,
            stock_quantity=10,
            reserved_quantity=2,
        )

        response = service_client.get(f"{url}?category_id={str(cat_b_id)}")

        assert response.status_code == status.HTTP_200_OK, response.json()
        items = response.json().get("items")
        item_ids = [item["id"] for item in items]

        assert str(p_in_cat_b.id) in item_ids
        assert str(p_in_cat_a.id) not in item_ids

    def test_catalog_filters_by_search(self, service_client, product_factory):
        url = reverse(self.url_name)

        p_search = product_factory(
            title="Unique Smartphone",
            description="Very unique description containing Smartphone",
            status=ProductStatus.MODERATED,
        )
        SKU.objects.create(
            product=p_search,
            name="sku_search",
            price=100,
            cost_price=80,
            stock_quantity=10,
            reserved_quantity=2,
        )

        p_other = product_factory(
            title="Standard TV",
            description="Just a regular television",
            status=ProductStatus.MODERATED,
        )
        SKU.objects.create(
            product=p_other,
            name="sku_other",
            price=100,
            cost_price=80,
            stock_quantity=10,
            reserved_quantity=2,
        )

        response = service_client.get(f"{url}?search=Smartphone")

        assert response.status_code == status.HTTP_200_OK
        items = response.json().get("items", [])
        item_ids = [item["id"] for item in items]

        assert str(p_search.id) in item_ids
        assert str(p_other.id) not in item_ids

    def test_catalog_filters_by_min_price_max_price(
        self, service_client, catalog_products
    ):
        url = reverse(self.url_name)
        response = service_client.get(f"{url}?min_price=125&max_price=175")

        assert response.status_code == status.HTTP_200_OK, response.json()
        data = response.json()

        items = data.get("items", [])
        item_ids = [item["id"] for item in items]

        assert str(catalog_products["visible_2"].id) in item_ids

        assert str(catalog_products["visible"].id) not in item_ids
        assert str(catalog_products["out_of_stock"].id) not in item_ids
        assert str(catalog_products["deleted"].id) not in item_ids
        assert str(catalog_products["created"].id) not in item_ids

    def test_catalog_filters_by_characteristics(
        self, service_client, catalog_products, product_factory
    ):
        url = reverse(self.url_name)

        p_search = product_factory(
            title="Unique Smartphone",
            description="Very unique description containing Smartphone",
            status=ProductStatus.MODERATED,
        )
        SKU.objects.create(
            product=p_search,
            name="sku_search",
            price=100,
            cost_price=80,
            stock_quantity=10,
            reserved_quantity=2,
        )
        ProductCharacteristics.objects.create(
            product_id=p_search, name="brand", value="Apple"
        )

        p_other = product_factory(
            title="Standard TV",
            description="Just a regular television",
            status=ProductStatus.MODERATED,
        )
        SKU.objects.create(
            product=p_other,
            name="sku_other",
            price=100,
            cost_price=80,
            stock_quantity=10,
            reserved_quantity=2,
        )
        ProductCharacteristics.objects.create(
            product_id=p_other, name="brand", value="Samsung"
        )

        response = service_client.get(f"{url}?filters[brand]=apple")

        assert response.status_code == status.HTTP_200_OK
        items = response.json().get("items", [])
        item_ids = [item["id"] for item in items]

        assert str(p_search.id) in item_ids
        assert str(p_other.id) not in item_ids

    def test_catalog_filters_by_seller_id(
        self, service_client, catalog_products, product_factory, test_user, test_category
    ):
        url = reverse(self.url_name)

        other_seller = Seller.objects.create(username="other", password="password123")

        p_search = product_factory(
            title="Unique Smartphone",
            description="Very unique description containing Smartphone",
            status=ProductStatus.MODERATED,
        )
        SKU.objects.create(
            product=p_search,
            name="sku_search",
            price=100,
            cost_price=80,
            stock_quantity=10,
            reserved_quantity=2,
        )

        p_other = Product.objects.create(
            title="Standard TV",
            description="Just a regular television",
            status=ProductStatus.MODERATED,
            category=test_category,
            seller=other_seller
        )
        SKU.objects.create(
            product=p_other,
            name="sku_other",
            price=100,
            cost_price=80,
            stock_quantity=10,
            reserved_quantity=2,
        )

        response = service_client.get(f"{url}?seller_id={test_user.id}")

        assert response.status_code == status.HTTP_200_OK
        items = response.json().get("items", [])
        item_ids = [item["id"] for item in items]

        assert str(p_search.id) in item_ids
        assert str(p_other.id) not in item_ids
