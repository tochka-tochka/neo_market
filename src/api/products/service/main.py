from typing import Dict, List, Union
import uuid
from src.models.product import Product, ProductStatus, Category
from src.models.user import Seller
from django.core.files.uploadedfile import UploadedFile
from src.serializes import ProductSerializer
from rest_framework import serializers
from django.db import transaction
import json

def get_all_products(seller: Seller) -> List[Product]:
    try:
        products = Product.objects.select_related('category').filter(seller=seller)
        serializer = ProductSerializer(products, many=True)
        return serializer.data
    except Exception as e:
        raise Exception(f"failed to get products: {e}")

def get_product(id: str, seller: Seller):
    try:
        product = Product.objects.select_related('category').get(id=id)
        if product.seller != seller:
            raise Exception("Access Denied")
        
        serializer = ProductSerializer(product) 
        
        return serializer.data
    except Product.DoesNotExist:
        raise Exception(f"Product with id {id} not found")
    except Exception as e:
        raise Exception(f"failed to get product: {e}")

@transaction.atomic
def create_product(data: Dict[str, str], image: Union[UploadedFile, None], seller: Seller) -> uuid:
    id = uuid.uuid4()

    chars = data["characteristics"]

    if isinstance(chars, str):
        try:
            chars = json.loads(chars)
        except json.JSONDecodeError:
            chars = {}
    try:
        Product.objects.create(
            id=id,
            title=data["title"],
            description=data["description"],
            image=image,
            category_id=data["category"],
            status=ProductStatus.CREATED,
            characteristics=chars,
            seller=seller
        )
    except Exception as e:
        raise Exception(f"faield to create product: {e}")
    return id

def update_product(data: Dict[str, str], image: Union[UploadedFile, None], seller: Seller):
    print(f"DEBUG update_product data: {data}")
    try:
        product = Product.objects.get(id=data.get("id"))

        if product.seller != seller:
            raise Exception("Access Denied")
        
        if data.get("title") is not None:
            product.title = data["title"]
        
        if data.get("description") is not None:
            product.description = data["description"]
        
        if data.get("category") is not None:
            category_id = data["category"]
            try:
                product.category = Category.objects.get(id=category_id)
            except Category.DoesNotExist:
                product.category = Category.objects.get(value=category_id)
        
        if data.get("characteristics") is not None:
            chars = data["characteristics"]
            if isinstance(chars, str):
                chars = json.loads(chars)
            product.characteristics = chars

        if image is not None:
            try:
                product.image = image
            except Exception as e:
                raise Exception(f"failed to update product image: {e}")
        
        product.save()
    except Product.DoesNotExist:
        raise Exception(f"Product with id {data.get('id')} not found")
    except Exception as e:
        raise Exception(f"failed to update product: {e}")
    
def delete_product(id: str, seller: Seller):
    try:
        product = Product.objects.get(id=id)
        if product.seller != seller:
            raise Exception("Access Denied")
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