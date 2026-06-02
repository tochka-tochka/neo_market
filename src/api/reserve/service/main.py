import json
from datetime import datetime

from django.db import transaction
from django.utils import timezone

from interservice_queues.producers import services_channel_producer
from src.models.product import SKU, Order, OrderItem, OrderStatus, ReserveOperations


class NotEnoughQunatity(Exception):
    def __init__(self, message, details):
        super().__init__(message)

        self.details = details


class NegativeQuantity(Exception):
    pass


class OrderNotFound(Exception):
    pass


@transaction.atomic
def reserve(idempotency_key, order_id, reserved_items):
    reserve = ReserveOperations.objects.filter(idempotency_key=idempotency_key).first()
    if reserve is not None:
        return json.loads(reserve.result)
    try:
        order = Order.objects.create(id=order_id, status=OrderStatus.RESERVED)

        failed_reserves = []

        for item in reserved_items:
            if item["quantity"] < 0:
                raise NegativeQuantity("negative quantity")

            sku = SKU.objects.select_for_update().get(id=item["sku_id"])

            if sku.stock_quantity - sku.reserved_quantity == 0:
                failed_reserves.append(
                    {
                        "sku_id": str(sku.id),
                        "requested": item["quantity"],
                        "available": sku.stock_quantity - sku.reserved_quantity,
                        "reason": "OUT_OF_STOCK",
                    }
                )
            elif sku.stock_quantity - sku.reserved_quantity - item["quantity"] < 0:
                failed_reserves.append(
                    {
                        "sku_id": str(sku.id),
                        "requested": item["quantity"],
                        "available": sku.stock_quantity - sku.reserved_quantity,
                        "reason": "INSUFFICIENT_STOCK",
                    }
                )

            elif sku.stock_quantity - sku.reserved_quantity - item["quantity"] == 0:
                print("MESSAGE SENT\n")
                services_channel_producer.product_b2c_notification(
                    data={"sku_id": str(sku.id), "event": "SKU_OUT_OF_STOCK"},
                    corrected=False,
                )

            sku.reserved_quantity += item["quantity"]
            sku.save()
            OrderItem.objects.create(order=order, sku=sku, quantity=item["quantity"])

        if len(failed_reserves) > 0:
            raise NotEnoughQunatity(
                "Failed to reserve some products", json.dumps(failed_reserves)
            )
        result = {
            "order_id": str(order.id),
            "status": "RESERVED",
            "reserved_at": str(datetime.now()),
        }
        ReserveOperations.objects.create(
            idempotency_key=idempotency_key, result=json.dumps(result)
        )
        return result
    except NotEnoughQunatity as e:
        raise e
    except Exception as e:
        raise Exception(f"failed to reserve sku: {e}")


@transaction.atomic
def unreserve(order_id, reserved_items):
    try:
        unreserve = ReserveOperations.objects.filter(idempotency_key=order_id).first()
        if unreserve is not None:
            return unreserve.result
        for item in reserved_items:
            sku = SKU.objects.select_for_update().get(id=item["sku_id"])
            if sku.reserved_quantity < item["quantity"]:
                raise NegativeQuantity()
            sku.reserved_quantity -= item["quantity"]
            sku.save()
        Order.objects.get(id=order_id).delete()
        result = {
            "order_id": str(order_id),
            "status": "UNRESERVED",
            "processed_at": str(datetime.now()),
        }
        ReserveOperations.objects.create(idempotency_key=order_id, result=result)
        return result
    except NegativeQuantity as e:
        raise e
    except Exception as e:
        raise Exception(f"failed to reserve sku: {e}")


@transaction.atomic
def fulfill(order_id, fullifed_items):
    order = Order.objects.filter(id=order_id).first()
    if order is None:
        raise OrderNotFound("order not found")
    if order.status == OrderStatus.FULFILLED:
        result = {
            "order_id": str(order_id),
            "status": "FULFILLED",
            "processed_at": str(order.processed_at),
        }
        return result
    try:
        for item in fullifed_items:
            sku = SKU.objects.select_for_update().get(id=item["sku_id"])
            if sku.reserved_quantity - item["quantity"] < 0:
                raise NotEnoughQunatity(
                    "Failed to fulfill order",
                    [
                        {
                            "sku_id": str(sku.id),
                            "requested": item["quantity"],
                            "available": sku.reserved_quantity,
                            "reason": "INSUFFICIENT_STOCK",
                        }
                    ],
                )

            sku.reserved_quantity -= item["quantity"]
            sku.stock_quantity -= item["quantity"]
            sku.save()
        order.status = OrderStatus.FULFILLED
        order.processed_at = timezone.now()
        order.save()
        result = {
            "order_id": str(order_id),
            "status": "FULFILLED",
            "processed_at": str(order.processed_at),
        }
        return result
    except OrderNotFound as e:
        raise e
    except NotEnoughQunatity as e:
        raise e
    except Exception as e:
        raise Exception(f"failed to reserve sku: {e}")
