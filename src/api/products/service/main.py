from typing import Dict, List, Any
import uuid
from src.models.product import Product, ProductStatus, ProductImage
from src.models import Category
from src.models.user import Seller
from django.core.files.uploadedfile import UploadedFile
from src.serializes import ProductSerializer
from django.db import transaction
import json

class InvalidCategoryId(Exception):
    pass

def get_all_products(seller: Seller):
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
def create_product(data: Dict[str, Any], images: List[UploadedFile], seller: Seller):
    product_id = uuid.uuid4()

    chars = data.get("characteristics", {})
    if isinstance(chars, str):
        try:
            chars = json.loads(chars)
        except json.JSONDecodeError:
            chars = {}

    category_id = data.get("category")
    if category_id:
        try:
            Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            raise InvalidCategoryId(f"Category with id {category_id} does not exist")

    try:
        product = Product.objects.create(
            id=product_id,
            title=data.get("title"),
            description=data.get("description"),
            category_id=data.get("category"),
            status=ProductStatus.CREATED,
            characteristics=chars,
            seller=seller
        )
        
        if images:
            image_objects = []
            for index, file in enumerate(images):
                image_objects.append(ProductImage(
                    product=product,
                    url=file,
                    order=index
                ))
            
            ProductImage.objects.bulk_create(image_objects)
        # moder_queue.product_moder_notification(str(product_id))

    except Exception as e:
        raise Exception(f"failed to create product: {e}")
        
    return ProductSerializer(product).data

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
                ProductImage.objects.filter(product=product).delete()
                image_objects = []
                for index, file in enumerate(images):
                    image_objects.append(ProductImage(
                        product=product,
                        url=file,
                        order=index
                    ))
                
                ProductImage.objects.bulk_create(image_objects)
            except Exception as e:
                raise Exception(f"failed to update product image: {e}")
        
        product.status = ProductStatus.ON_MODERATION
        
        product.save()

        # moder_queue.product_moder_notification(product.id)
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
    
def get_categories():
    try:
        categories = Category.objects.all().values(
            'id', 'parent_id', 'value'
        )
        return list(categories)
    except Exception as e:
        raise Exception(f"failed to get categories: {e}")

def get_category(id: uuid.UUID) -> Category:
    try:
        category = Category.objects.get(id=id)
        return category
    except Exception as e:
        raise Exception(f"failed to get category: {e}")