from typing import Dict, List, Union, Any
import uuid
from src.models.product import Product, ProductStatus, Category, Image
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
def create_product(data: Dict[str, Any], images: List[UploadedFile], seller: Seller) -> uuid.UUID:
    # 1. Генерация ID (лучше позволить модели сделать это, но если нужно вручную):
    product_id = uuid.uuid4()

    # 2. Обработка характеристик
    chars = data.get("characteristics", {})
    if isinstance(chars, str):
        try:
            chars = json.loads(chars)
        except json.JSONDecodeError:
            chars = {}

    try:
        # 3. Создаем продукт
        product = Product.objects.create(
            id=product_id,
            title=data["title"],
            description=data["description"],
            category_id=data["category"], # Убедитесь, что здесь UUID категории
            status=ProductStatus.CREATED,
            characteristics=chars,
            seller=seller
        )

        # 4. Создаем изображения
        if images:
            image_objects = []
            for index, file in enumerate(images):
                # Явно указываем именованные аргументы
                image_objects.append(Image(
                    product=product,
                    url=file,
                    order=index
                ))
            
            Image.objects.bulk_create(image_objects)

    except Exception as e:
        raise Exception(f"failed to create product: {e}")
        
    return product_id

@transaction.atomic
def update_product(data: Dict[str, str], images: List[UploadedFile], seller: Seller):
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

        if images is not None:
            try:
                Image.objects.filter(product=product).delete()
                image_objects = []
                for index, file in enumerate(images):
                    image_objects.append(Image(
                        product=product,
                        url=file,
                        order=index
                    ))
                
                Image.objects.bulk_create(image_objects)
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