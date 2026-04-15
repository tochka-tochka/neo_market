from typing import Dict, Any
import uuid
from src.models.product import Product, SKU
from django.db import transaction
import json

@transaction.atomic
def create_sku(data: Dict[str, Any], seller) -> uuid.UUID:
    sku_id = uuid.uuid4()

    chars = data.get("characteristics", {})
    if isinstance(chars, str):
        try:
            chars = json.loads(chars)
        except json.JSONDecodeError:
            chars = {}

    product = Product.objects.get(id=data.get("product_id"))

    if seller == product.seller:

        try:
            SKU.objects.create(
                id=sku_id,
                name=data["name"],
                price=data["price"],
                active_quantity=data["active_quantity"],
                characteristics=chars,
                product=product
            )

        except Exception as e:
            raise Exception(f"failed to create SKU: {e}")
            
        return sku_id
    else:
        raise Exception("Access Denied")

@transaction.atomic
def update_sku(data: Dict[str, str], seller):
    print(f"DEBUG update_sku data: {data}")
    try:
        sku = SKU.objects.get(id=data.get("id"))
        
        if sku.product.seller == seller:

            if data.get("name") is not None:
                sku.name = data["name"]
            
            if data.get("price") is not None:
                sku.price = int(data["price"])
            
            if data.get("active_quantity") is not None:
                sku.active_quantity = int(data["active_quantity"])
            
            if data.get("characteristics") is not None:
                chars = data["characteristics"]
                if isinstance(chars, str):
                    chars = json.loads(chars)
                sku.characteristics = chars
            
            sku.save()

        else:
            raise Exception('Access Denied')
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
