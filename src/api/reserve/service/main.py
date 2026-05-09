import json
from django.template.context_processors import request
from django.db import transaction
from src.models.product import SKU, ReserveOperations
from rabbitmq_prod.moder import moder_queue

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
        return reserve.result
    try:
        result = []
        for item in reserved_items:
            sku = SKU.objects.get(id=item["sku_id"])
            
            if sku.active_quantity - item["quantity"] < 0:
                raise NotEnoughQunatity("Not enough quantity", str(sku.id), item["quantity"], sku.active_quantity)
                
            if sku.active_quantity - item["quantity"] == 0:
                print("MESSAGE SENT\n")
                moder_queue.product_b2c_notification(data={
                    "sku_id": str(sku.id),
                    "event": "SKU_OUT_OF_STOCK"
                }, corrected=False)
                
            sku.active_quantity -= item["quantity"]
            sku.reserved_quantity += item["quantity"]
            result.append({
                "sku_id": str(sku.id),
                "reserved_quantity": sku.reserved_quantity + item["quantity"],
                "remaning_stock": sku.active_quantity - item["quantity"]
            })
            sku.save()
        ReserveOperations.objects.create(
            idempotency_key=idempotency_key,
            result=json.dumps(result)
        )
        return result
    except NotEnoughQunatity as e:
        raise e
    except Exception as e:
        raise Exception(f"failed to reserve sku: {e}")

@transaction.atomic
def unreserve(reserved_items):
    try:
        for item in reserved_items:
            sku = SKU.objects.get(id=item["sku_id"])
            sku.active_quantity += item["quantity"]
            sku.reserved_quantity -= item["quantity"]
            sku.save()
    except Exception as e:
        raise Exception(f"failed to reserve sku: {e}")
