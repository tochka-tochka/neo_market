from typing import Dict, List, Any
import uuid
from src.models.product import Product, ProductStatus, ProductImage
from src.models import Category
from src.models.user import Seller
from django.core.files.uploadedfile import UploadedFile
from src.serializes import ProductSerializer
from django.db import transaction
import json
from rabbitmq_prod.moder import moder_queue
from datetime import datetime

class InvalidCategoryId(Exception):
    pass

class HardBlockerProduct(Exception):
    pass

class AccessDenied(Exception):
    pass

class ProductAlreadyDeleted(Exception):
    pass

def get_all_products(seller: Seller):
    try:
        products = Product.objects.select_related('category').filter(seller=seller, deleted=False)
        serializer = ProductSerializer(products, many=True)
        return serializer.data
    except Exception as e:
        raise Exception(f"failed to get products: {e}")

def get_product(id: str, seller: Seller):
    try:
        product = Product.objects.select_related('category').get(id=id, seller=seller, deleted=False)
        
        serializer = ProductSerializer(product) 
        
        return serializer.data
    except Product.DoesNotExist as e:
        raise e
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

    except Exception as e:
        raise Exception(f"failed to create product: {e}")
        
    return ProductSerializer(product).data

@transaction.atomic
def update_product(data: Dict[str, str], images: List[UploadedFile], seller: Seller):
    try:
        product = Product.objects.get(id=data.get("id"))

        if product.status == ProductStatus.HARD_BLOCKED:
            raise HardBlockerProduct("Product is hard-blocked")

        if product.seller != seller:
            raise AccessDenied("Access Denied")
        
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

        idempotency_key = str(uuid.uuid4())
        moder_queue.product_moder_notification(data={
            "idempotency_key": idempotency_key,
            "product_id": str(product.id),
            "seller_id": str(seller.id),
            "event": "EDITED",
            "date": str(datetime.now()),
        }, corrected=True)
        
        product.save()

        return ProductSerializer(product).data

    except AccessDenied:
        raise HardBlockerProduct("failed to update product: You are not product's owner")
    except HardBlockerProduct:
        raise HardBlockerProduct("failed to update product: Product is hard-blocked")
    except Product.DoesNotExist:
        raise Exception(f"Product with id {data.get('id')} not found")
    except Exception as e:
        raise Exception(f"failed to update product: {e}")
    
def delete_product(id: str, seller: Seller):
    try:
        product = Product.objects.get(id=id)
        if product.seller != seller:
            raise AccessDenied("Access Denied")

        if product.deleted:
            raise ProductAlreadyDeleted("Product already deleted")
        product.deleted = True
        product.save()


        moder_queue.product_moder_notification(data={
            "idempotency_key": str(uuid.uuid4()),
            "product_id": str(product.id),
            "seller_id": str(seller.id),
            "event": "DELETED",
            "date": str(datetime.now()),
        }, corrected=True)

        product_serializer = ProductSerializer(product).data
                
        moder_queue.product_b2c_notification(data={
            "idempotency_key": str(uuid.uuid4()),
            "product_id": str(product.id),
            "sku_ids": list(map(lambda sku: sku['id'], product_serializer['skus'])),
            "event": "PRODUCT_DELETED",
            "date": str(datetime.now()),
        }, corrected=True)
    except AccessDenied as e:
        raise e
    except ProductAlreadyDeleted as e:
        raise e
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