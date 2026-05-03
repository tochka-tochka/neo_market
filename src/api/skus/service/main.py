import json
import uuid
from datetime import datetime
from typing import Any, Dict, List

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

from rabbitmq_prod.moder import ModerQueue
from src.models.product import SKU, Product, ProductStatus, SKUImage
from src.serializes import SKUSerializer


class BlockedProductException(Exception):
    pass


@transaction.atomic
def create_sku(data: Dict[str, Any], images: List[UploadedFile], seller):

    chars = data.get("characteristics", {})
    if isinstance(chars, str):
        try:
            chars = json.loads(chars)
        except json.JSONDecodeError:
            chars = {}

    product = Product.objects.get(id=data.get("product_id"))

    if seller == product.seller:
        try:
            if product.status == ProductStatus.HARD_BLOCKED:
                raise BlockedProductException("This product hard-blocked")

            sku = SKU.objects.create(
                name=data["name"],
                price=data["price"],
                cost_price=data["price"],
                discount=data["discount"],
                active_quantity=data["active_quantity"],
                characteristics=chars,
                product=product,
            )

            if images:
                for index, image in enumerate(images):
                    SKUImage.objects.create(sku=sku, url=image, order=index)

            if product.status == ProductStatus.CREATED:
                idempotency_key = str(uuid.uuid4())
                moder_queue = ModerQueue()
                moder_queue.product_moder_notification(
                    data={
                        "idempotency_key": idempotency_key,
                        "product_id": str(product.id),
                        "seller_id": str(seller.id),
                        "event": "EDITED",
                        "date": str(datetime.now()),
                    },
                    corrected=False,
                )
                product.status = ProductStatus.ON_MODERATION
                product.save()

            if product.status == ProductStatus.ON_MODERATION:
                moder_queue = ModerQueue()
                moder_queue.product_moder_notification(
                    data={
                        "idempotency_key": str(uuid.uuid4()),
                        "product_id": str(product.id),
                        "seller_id": str(seller.id),
                        "event": "EDITED",
                        "date": str(datetime.now()),
                    },
                    corrected=True,
                )

        except BlockedProductException as e:
            raise e
        except Exception as e:
            raise Exception(f"failed to create SKU: {e}")

        return SKUSerializer(sku).data
    else:
        raise Exception("Access Denied")


@transaction.atomic
def update_sku(data: Dict[str, str], images: List[UploadedFile], seller):
    try:
        sku = SKU.objects.get(id=data.get("id"))

        if sku.product.seller == seller:
            if data.get("name") is not None:
                sku.name = data["name"]

            if data.get("price") is not None:
                sku.price = int(data["price"])

            if data.get("cost_price") is not None:
                sku.price = int(data["cost_price"])

            if data.get("discount") is not None:
                sku.price = int(data["discount"])

            if data.get("active_quantity") is not None:
                sku.active_quantity = int(data["active_quantity"])

            if data.get("characteristics") is not None:
                chars = data["characteristics"]
                if isinstance(chars, str):
                    chars = json.loads(chars)
                sku.characteristics = chars

            if images:
                SKUImage.objects.filter(sku=sku).delete()
                for index, image in enumerate(images):
                    SKUImage.objects.create(sku=sku, url=image, order=index)

            sku.save()

        else:
            raise Exception("Access Denied")
    except SKU.DoesNotExist:
        raise Exception(f"SKU with id {data.get('id')} not found")
    except Exception as e:
        raise Exception(f"failed to update sku: {e}")


@transaction.atomic
def delete_sku(id, seller):
    sku = SKU.objects.get(id=id)

    if sku.product.seller == seller:
        try:
            sku.delete()
        except Exception as e:
            raise Exception(f"failed to delete sku: {e}")
    else:
        raise Exception("Access Denied")
