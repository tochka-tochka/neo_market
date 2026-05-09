import uuid
import pytest
from django.urls import reverse
from rest_framework import status

from src.models.product import ProductStatus, SKU, Product

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

@pytest.mark.django_db
class TestCatalogProducts(BaseTestUtil):
    
    url_name = "products" 

    def test_catalog_returns_moderated_in_stock_products(self, service_client, catalog_products):
        url = reverse(self.url_name)
        response = service_client.get(url)

        assert response.status_code == status.HTTP_200_OK
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
            SKU.objects.create(product=p1, name="sku_cheap", price=100, cost_price=80, active_quantity=10)
            
            p2 = product_factory(title="Product Expensive", status=ProductStatus.MODERATED)
            SKU.objects.create(product=p2, name="sku_exp", price=500, cost_price=400, active_quantity=10)
            
            p3 = product_factory(title="Product Medium", status=ProductStatus.MODERATED)
            SKU.objects.create(product=p3, name="sku_med", price=300, cost_price=200, active_quantity=10)
    
            response = service_client.get(f"{url}?sort=price_desc")
            
            assert response.status_code == status.HTTP_200_OK
            items = response.json().get("items", [])

            test_product_ids = [str(p1.id), str(p2.id), str(p3.id)]
            sorted_ids = [item["id"] for item in items if item["id"] in test_product_ids]
            
            assert sorted_ids == [str(p2.id), str(p3.id), str(p1.id)]
    
    def test_catalog_filters_by_category(self, service_client, product_factory, test_user):
        url = reverse(self.url_name)
        
        from src.models.product import Category
        cat_b_id = uuid.uuid4()
        cat_b = Category.objects.create(
            id=cat_b_id, 
            value="Another Category", 
            slug="another_category"
        )
        
        p_in_cat_a = product_factory(title="Cat A Product", status=ProductStatus.MODERATED)
        SKU.objects.create(product=p_in_cat_a, name="sku_a", price=100, cost_price=80, active_quantity=10)
        
        p_in_cat_b = Product.objects.create(
            title="Approved Product", 
            category=cat_b, 
            seller=test_user, 
            status=ProductStatus.MODERATED
        )
        SKU.objects.create(product=p_in_cat_b, name="sku_b", price=100, cost_price=80, active_quantity=10)

        response = service_client.get(f"{url}?category={str(cat_b_id)}")
        
        assert response.status_code == status.HTTP_200_OK
        items = response.json().get("items")
        item_ids = [item["id"] for item in items]
        
        assert str(p_in_cat_b.id) in item_ids
        assert str(p_in_cat_a.id) not in item_ids

    def test_catalog_filters_by_search(self, service_client, product_factory):
        url = reverse(self.url_name)
        
        p_search = product_factory(
            title="Unique Smartphone", 
            description="Very unique description containing Smartphone", 
            status=ProductStatus.MODERATED
        )
        SKU.objects.create(product=p_search, name="sku_search", price=100, cost_price=80, active_quantity=10)
        
        p_other = product_factory(
            title="Standard TV", 
            description="Just a regular television", 
            status=ProductStatus.MODERATED
        )
        SKU.objects.create(product=p_other, name="sku_other", price=100, cost_price=80, active_quantity=10)

        response = service_client.get(f"{url}?search=Smartphone")
        
        assert response.status_code == status.HTTP_200_OK
        items = response.json().get("items", [])
        item_ids = [item["id"] for item in items]
        
        assert str(p_search.id) in item_ids
        assert str(p_other.id) not in item_ids