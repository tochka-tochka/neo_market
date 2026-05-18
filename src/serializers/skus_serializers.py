from django.core.validators import MinValueValidator
from rest_framework import serializers
from src.validators.main import validate_characteristics

from src.models.product import (
    SKU,
    Product,
    SKUImage
)

class SKUImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKUImage
        fields = ["id", "url", "ordering"]

class ProductIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id"]


class SKUSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(source="product.id", read_only=True)
    price = serializers.IntegerField(validators=[MinValueValidator(0)])
    images = SKUImageSerializer(many=True, read_only=True)
    characteristics = serializers.JSONField(
        required=False, allow_null=True, validators=[validate_characteristics]
    )

    class Meta:
        model = SKU
        fields = [
            "id",
            "product_id",
            "name",
            "price",
            "cost_price",
            "discount",
            "stock_quantity",
            "active_quantity",
            "reserved_quantity",
            "article",
            "images",
            "characteristics",
            "created_at",
            "updated_at"
        ]

class PublicSKUSerializer(serializers.ModelSerializer):
    product_id = serializers.UUIDField(source="product.id", read_only=True)
    price = serializers.IntegerField(validators=[MinValueValidator(0)])
    active_quantity = serializers.IntegerField(validators=[MinValueValidator(0)])
    images = SKUImageSerializer(many=True, read_only=True)
    characteristics = serializers.JSONField(
        required=False, allow_null=True, validators=[validate_characteristics]
    )

    class Meta:
        model = SKU
        fields = [
            "id",
            "product_id",
            "name",
            "price",
            "active_quantity",
            "images",
            "characteristics",
        ]