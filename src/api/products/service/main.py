from typing import Dict, List
import uuid
from src.models.product import Product, ProductStatus, Characteristic, Category
from src.serializes import ProductSerializer
from rest_framework import serializers
from django.db import transaction

def get_all_products() -> List[Product]:
    try:
        products = Product.objects.select_related('category').all()
        serializer = ProductSerializer(products, many=True)
        return serializer.data
    except Exception as e:
        raise Exception(f"failed to get products: {e}")

def get_product(id: str):
    try:
        product = Product.objects.select_related('category').prefetch_related('characteristics').get(id=id)
        
        serializer = ProductSerializer(product) 
        
        return serializer.data
    except Product.DoesNotExist:
        raise Exception(f"Product with id {id} not found")
    except Exception as e:
        raise Exception(f"failed to get product: {e}")

@transaction.atomic
def create_product(data: Dict[str, str], image: bytes) -> uuid:
    id = uuid.uuid4()
    try:
        Product.objects.create(
            id=id,
            title=data["title"],
            description=data["description"],
            category_id=data["category"],
            status=ProductStatus.CREATED,
        )
    except Exception as e:
        raise Exception(f"faield to create product: {e}")
    return id

def create_char(data: Dict[str, str]) -> uuid:
    id = uuid.uuid4
    try:
        Characteristic.objects.create(
            product_id = data["product"],
            name = data["name"],
            value = data["value"]
        )
    except Exception as e:
        raise Exception(f"faield to create product: {e}")
    return id

def update_product(data: Dict[str, str], image: bytes):
    try:
        product = Product.objects.get(id=data["id"])
        for key, value in data.items():
            if value is not None and key != "id":
                setattr(product, key, value)
        product.save()
    except Exception as e:
        raise Exception(f"failed to update product: {e}")
    
def delete_product(id: str):
    try:
        product = Product.objects.get(id=id)
        product.delete()
    except Exception as e:
        raise Exception(f"failed to delete product: {e}")
    
def get_categories() -> List[Category]:
    try:
        categories = Category.objects.all().values(
            'id', 'product', 'value'
        )
        return list(categories)
    except Exception as e:
        raise Exception(f"failed to get categories: {e}")