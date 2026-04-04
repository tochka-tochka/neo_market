from typing import Dict
import uuid
from src.models.product import Product, ProductStatus

def get_product(id: str) -> Product:
    try:
        product = Product.objects.get(id=id)
        return product
    except Exception as e:
        raise Exception(f"failed to get product: {e}")

def create_product(data: Dict[str, str], image: bytes) -> uuid:
    id = uuid.uuid4()
    try:
        Product.objects.create(
            id=id,
            title=data["title"],
            description=data["description"] | "",
            status=ProductStatus.CREATED
        )
    except Exception as e:
        raise Exception(f"faield to create product: {e}")
    return id

def update_product(data: Dict[str, str], image: bytes):
    try:
        product = Product.objects.get(id=data["id"])
        for key, value in data.items():
            if value is not None and key != "id":
                setattr(product, key, value)
        product.save()
    except Exception as e:
        raise Exception(f"failed to update product: {e}")
    
def delete_product(id: str):
    try:
        product = Product.objects.get(id=id)
        product.delete()
    except Exception as e:
        raise Exception(f"failed to delete product: {e}")