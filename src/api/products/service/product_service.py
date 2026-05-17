import json
import uuid
from datetime import datetime
from typing import Any, Dict, List

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from django.db.models import Q
from django.template.context_processors import request

from interservice_queues.producers import services_channel_producer
from src.models import Category
from src.models.product import Product, ProductImage, ProductStatus
from src.models.user import Seller
from src.serializers.product_serializers import (
    CreateProductSerializer,
    ProductSerializer,
)


class InvalidCategoryId(Exception):
    pass


class HardBlockerProduct(Exception):
    pass


class AccessDenied(Exception):
    pass


class ProductAlreadyDeleted(Exception):
    pass


def get_seller_products(
    search: str | None,
    status: ProductStatus | None,
    limit: int | None,
    offset: int | None,
    seller: Seller,
    deleted: bool | None,
):
    try:
        query = Q(seller=seller)

        if deleted is None or deleted != "true":
            query &= Q(deleted=False)

        if search is not None:
            query &= Q(title__icontains=search) | Q(description__icontains=search)

        if status is not None:
            query &= Q(status=status)

        if limit is None:
            limit = 20

        if offset is None:
            offset = 0

        products = Product.objects.select_related("category").filter(query)[
            offset : offset + limit
        ]
        serializer = ProductSerializer(products, many=True)
        return serializer.data, limit, offset
    except Exception as e:
        raise Exception(f"failed to get products: {e}")


def get_product(id: str, seller: Seller):
    try:
        product = Product.objects.select_related("category").get(
            id=id, seller=seller, deleted=False
        )

        serializer = ProductSerializer(product)

        return serializer.data
    except Product.DoesNotExist as e:
        raise e
    except Exception as e:
        raise Exception(f"failed to get product: {e}")


@transaction.atomic
def create_product(data: Dict[str, Any], seller: Seller):
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
            slug=data.get("slug"),
            category_id=data.get("category"),
            status=ProductStatus.CREATED,
            characteristics=chars,
            seller=seller,
        )

        images = data.get("images")

        if images:
            image_objects = []
            for index, image in enumerate(images):
                image_objects.append(
                    ProductImage(
                        product=product, url=image["url"], ordering=image["ordering"]
                    )
                )

            ProductImage.objects.bulk_create(image_objects)

    except Exception as e:
        raise Exception(f"failed to create product: {e}")

    return CreateProductSerializer(product).data


@transaction.atomic
def update_product(data: Dict[str, str], seller: Seller):
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

        images = data.get("images")
        if images is not None:
            try:
                ProductImage.objects.filter(product=product).delete()
                image_objects = []
                for index, file in enumerate(images):
                    image_objects.append(
                        ProductImage(product=product, url=file, ordering=index)
                    )

                ProductImage.objects.bulk_create(image_objects)
            except Exception as e:
                raise Exception(f"failed to update product image: {e}")

        if product.status != ProductStatus.CREATED:
            idempotency_key = str(uuid.uuid4())
            services_channel_producer.product_moder_notification(
                data={
                    "idempotency_key": idempotency_key,
                    "product_id": str(product.id),
                    "seller_id": str(seller.id),
                    "event": "EDITED",
                    "date": str(datetime.now()),
                },
                corrected=True,
            )

        product.status = ProductStatus.ON_MODERATION

        product.save()

        return ProductSerializer(product).data

    except AccessDenied:
        raise HardBlockerProduct(
            "failed to update product: You are not product's owner"
        )
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

        if product.status == ProductStatus.HARD_BLOCKED:
            raise HardBlockerProduct("Product is hard-blocked")

        if product.deleted:
            raise ProductAlreadyDeleted("Product already deleted")
        product.deleted = True
        product.save()

        services_channel_producer.product_moder_notification(
            data={
                "idempotency_key": str(uuid.uuid4()),
                "product_id": str(product.id),
                "seller_id": str(seller.id),
                "event": "DELETED",
                "date": str(datetime.now()),
            },
            corrected=True,
        )

        product_serializer = ProductSerializer(product).data

        services_channel_producer.product_b2c_notification(
            data={
                "idempotency_key": str(uuid.uuid4()),
                "product_id": str(product.id),
                "sku_ids": list(map(lambda sku: sku["id"], product_serializer["skus"])),
                "event": "PRODUCT_DELETED",
                "date": str(datetime.now()),
            },
            corrected=True,
        )
    except AccessDenied as e:
        raise e
    except HardBlockerProduct as e:
        raise e
    except ProductAlreadyDeleted as e:
        raise e
    except Exception as e:
        raise Exception(f"failed to delete product: {e}")
