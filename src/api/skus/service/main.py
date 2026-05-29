import json
import uuid
from datetime import datetime
from functools import partial
from typing import Any, Dict

from django.db import transaction

from interservice_queues.producers import services_channel_producer
from src.models.product import SKU, Product, ProductStatus, SKUImage, SkuCharacteristics
from src.serializers.product_serializers import ProductSerializer
from src.serializers.skus_serializers import SKUSerializer


class BlockedProductException(Exception):
    pass


class AccessDenied(Exception):
    pass


class SKUNotFound(Exception):
    pass


class ProductNotFound(Exception):
    pass


class SKUGotActiveReserves(Exception):
    pass


@transaction.atomic
def create_sku(data: Dict[str, Any], seller):

    chars = data.get("characteristics", {})
    if isinstance(chars, str):
        try:
            chars = json.loads(chars)
        except json.JSONDecodeError:
            chars = {}
    try:
        for char in chars:
            char["id"] = str(uuid.uuid4())
        product = Product.objects.filter(id=data.get("product_id")).first()

        if product is None:
            raise ProductNotFound("Product not found")

        if product.status == ProductStatus.HARD_BLOCKED:
            raise BlockedProductException("This product hard-blocked")

        if product.seller != seller:
            raise AccessDenied("Access Denied")

        if not SKU.objects.filter(product=product).exists():
            idempotency_key = str(uuid.uuid4())
            transaction.on_commit(
                partial(
                    services_channel_producer.product_moder_notification,
                    data={
                        "idempotency_key": idempotency_key,
                        "product_id": str(product.id),
                        "seller_id": str(seller.id),
                        "event": "CREATED",
                        "date": str(datetime.now()),
                    },
                    corrected=False,
                )
            )
        else:
            idempotency_key = str(uuid.uuid4())
            transaction.on_commit(
                partial(
                    services_channel_producer.product_moder_notification,
                    data={
                        "idempotency_key": idempotency_key,
                        "product_id": str(product.id),
                        "seller_id": str(seller.id),
                        "event": "EDITED",
                        "date": str(datetime.now()),
                    },
                    corrected=False,
                )
            )
        product.status = ProductStatus.ON_MODERATION
        product.save()

        sku = SKU.objects.create(
            name=data["name"],
            price=data["price"],
            cost_price=data["cost_price"],
            article=data["article"],
            discount=data["discount"],
            product=product,
        )

        images = data.get("images")
        if images:
            for image in images:
                SKUImage.objects.create(
                    sku=sku, url=image["url"], ordering=image["ordering"]
                )

        sku.characteristics.set([
            SkuCharacteristics.objects.create(**chr, sku_id=sku) for chr in chars
        ])
    except ProductNotFound as e:
        raise e
    except AccessDenied as e:
        raise e
    except BlockedProductException as e:
        raise e
    except Exception as e:
        raise Exception(f"failed to create SKU: {e}")

    return SKUSerializer(sku).data


@transaction.atomic
def update_sku(data: Dict[str, Any], seller):
    try:
        sku = SKU.objects.get(id=data.get("id"))
        product = Product.objects.get(id=sku.product.id)
        if sku.product.seller != seller:
            raise AccessDenied("Product does not belong to the authenticated seller")

        if product.status == ProductStatus.HARD_BLOCKED:
            raise BlockedProductException("This product hard-blocked")

        if data.get("name") is not None:
            sku.name = data["name"]

        if data.get("price") is not None:
            sku.price = int(data["price"])

        if data.get("cost_price") is not None:
            sku.cost_price = int(data["cost_price"])

        if data.get("discount") is not None:
            sku.discount = int(data["discount"])

        
        chars = data["characteristics"]

        images = data.get("images")
        if images:
            SKUImage.objects.filter(sku=sku).delete()
            for image in images:
                SKUImage.objects.create(
                    sku=sku, url=image["url"], ordering=image["ordering"]
                )

        sku.characteristics.all().delete()
        sku.characteristics.set([
            SkuCharacteristics.objects.create(**chr, sku_id=sku) for chr in chars
        ])

        sku.save()
        product = Product.objects.get(id=sku.product.id)
        product.status = ProductStatus.ON_MODERATION
        product.save()

        services_channel_producer.product_moder_notification(
            data={
                "idempotency_key": str(uuid.uuid4()),
                "product_id": str(product.id),
                "seller_id": str(seller.id),
                "event": "EDITED",
                "date": str(datetime.now()),
            },
            corrected=True,
        )

        return SKUSerializer(sku).data
    except SKU.DoesNotExist as e:
        raise e
    except AccessDenied as e:
        raise e
    except BlockedProductException as e:
        raise e
    except Exception as e:
        raise Exception(f"failed to update sku: {e}")


@transaction.atomic
def delete_sku(id, seller):
    try:
        sku = SKU.objects.select_for_update().filter(id=id).first()
        if sku is None:
            raise SKUNotFound("SKU not found")

        product = sku.product
        if product.seller != seller:
            raise AccessDenied("SKU does not belong to the authenticated seller")

        if product.status == ProductStatus.HARD_BLOCKED:
            raise BlockedProductException(
                "SKU does not belong to the authenticated seller"
            )

        if sku.reserved_quantity > 0:
            raise SKUGotActiveReserves("Cannot delete SKU with active reserves")

        sku_id = sku.id
        if sku.stock_quantity > 0 and product.status == ProductStatus.MODERATED:
            services_channel_producer.product_b2c_notification(
                data={
                    "idempotency_key": str(uuid.uuid4()),
                    "product_id": str(product.id),
                    "sku_id": str(sku_id),
                    "event": "SKU_OUT_OF_STOCK",
                    "date": str(datetime.now()),
                },
                corrected=True,
            )
        sku.delete()

        product.refresh_from_db()
        if len(product.skus.all()) == 0:
            if product.status == ProductStatus.ON_MODERATION:
                services_channel_producer.product_moder_notification(
                    data={
                        "idempotency_key": str(uuid.uuid4()),
                        "product_id": str(product.id),
                        "sku_id": str(sku_id),
                        "seller_id": str(seller.id),
                        "event": "DELETED",
                        "date": str(datetime.now()),
                    },
                    corrected=True,
                )
                product.status = ProductStatus.CREATED
        product.save()

    except SKUNotFound as e:
        raise e
    except BlockedProductException as e:
        raise e
    except AccessDenied as e:
        raise e
    except SKUGotActiveReserves as e:
        raise e
    except Exception as e:
        raise Exception(f"failed to delete sku: {e}")
