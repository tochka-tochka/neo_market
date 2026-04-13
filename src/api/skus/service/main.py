from typing import Dict, Any
import uuid
from src.models.product import Product, SKU
from django.db import transaction
import json

@transaction.atomic
def create_sku(data: Dict[str, Any]) -> uuid.UUID:
    # 1. Генерация ID (лучше позволить модели сделать это, но если нужно вручную):
    sku_id = uuid.uuid4()

    # 2. Обработка характеристик
    chars = data.get("characteristics", {})
    if isinstance(chars, str):
        try:
            chars = json.loads(chars)
        except json.JSONDecodeError:
            chars = {}

    product = Product.objects.get(id=data.get("product_id"))

    try:
        # 3. Создаем SKU
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

@transaction.atomic
def update_sku(data: Dict[str, str]):
    print(f"DEBUG update_sku data: {data}")
    try:
        sku = SKU.objects.get(id=data.get("id"))
        
        if data.get("name") is not None:
            sku.name = data["name"]
        
        if data.get("price") is not None:
            sku.price = int(data["price"])
        
        if data.get("activeQuantity") is not None:
            sku.active_quantity = int(data["active_quantity"])
        
        if data.get("characteristics") is not None:
            chars = data["characteristics"]
            if isinstance(chars, str):
                chars = json.loads(chars)
            sku.characteristics = chars
        
        sku.save()
    except SKU.DoesNotExist:
        raise Exception(f"SKU with id {data.get('id')} not found")
    except Exception as e:
        raise Exception(f"failed to update sku: {e}")