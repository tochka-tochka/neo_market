from datetime import datetime
import json

from django.db import transaction

from interservice_queues.producers import services_channel_producer
from src.models.product import SKU, ReserveOperations, Order, OrderItem, OrderStatus


class NotEnoughQunatity(Exception):
    def __init__(self, message, sku_id, requested, available):
        super().__init__(message)

        self.sku_id = sku_id
        self.requested = requested
        self.available = available


@transaction.atomic
def reserve(idempotency_key, reserved_items):
    reserve = ReserveOperations.objects.filter(idempotency_key=idempotency_key).first()
    if reserve is not None:
        return json.loads(reserve.result)
    try:
        order = Order.objects.create(status = OrderStatus.RESERVED)
        for item in reserved_items:
            sku = SKU.objects.get(id=item["sku_id"])

            if sku.active_quantity - item["quantity"] < 0:
                raise NotEnoughQunatity(
                    "Not enough quantity",
                    str(sku.id),
                    item["quantity"],
                    sku.active_quantity,
                )

            if sku.active_quantity - item["quantity"] == 0:
                print("MESSAGE SENT\n")
                services_channel_producer.product_b2c_notification(
                    data={"sku_id": str(sku.id), "event": "SKU_OUT_OF_STOCK"},
                    corrected=False,
                )

            sku.active_quantity -= item["quantity"]
            sku.reserved_quantity += item["quantity"]
            sku.save()
            OrderItem.objects.create(order=order, sku=sku, quantity=item["quantity"])
        result = {
            "order_id": str(order.id),
            "status": "RESERVED",
            "reserved_at": str(datetime.now())
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
        for item in reserved_items:
            sku = SKU.objects.get(id=item["sku_id"])
            sku.active_quantity += item["quantity"]
            sku.reserved_quantity -= item["quantity"]
            sku.save()
        Order.objects.get(id=order_id).delete()
        result = {
            "order_id": str(order_id),
            "status": "UNRESERVED",
            "reserved_at": str(datetime.now())
        }
        return result
    except Exception as e:
        raise Exception(f"failed to reserve sku: {e}")


# @transaction.atomic
# def fullify(order_id, fullifed_items):
#     reserve = FullifiedOrders.objects.filter(order_id=order_id).first()
#     if reserve is not None:
#         return
#     try:
#         for item in fullifed_items:
#             sku = SKU.objects.get(id=item["sku_id"])
#             if sku.active_quantity - item["quantity"] < 0:
#                 raise NotEnoughQunatity(
#                     "Not enough quantity",
#                     str(sku.id),
#                     item["quantity"],
#                     sku.active_quantity,
#                 )

#             sku.reserved_quantity -= item["quantity"]
#             sku.save()
#         FullifiedOrders.objects.create(order_id=order_id)
#     except NotEnoughQunatity as e:
#         raise e
#     except Exception as e:
#         raise Exception(f"failed to reserve sku: {e}")
