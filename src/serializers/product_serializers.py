from rest_framework import serializers

from src.models.product import (
    Product,
    ProductFieldReport,
    ProductImage,
)
from src.models.user import Seller
from src.validators.main import validate_characteristics
from src.serializers.skus_serializers import SKUSerializer, PublicSKUSerializer
from src.serializers.category_seializers import CategorySerializer 

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "product", "url", "order", "created_at"]

class ProductFieldReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductFieldReport
        fields = ["sku", "field", "comment"]


class SellerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ["id", "username"]


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    seller = SellerListSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    skus = SKUSerializer(many=True, read_only=True)
    characteristics = serializers.JSONField(
        required=False, allow_null=True, validators=[validate_characteristics]
    )
    field_reports = ProductFieldReportSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "description",
            "status",
            "blocking_reason",
            "field_reports",
            "seller",
            "images",
            "characteristics",
            "category",
            "skus",
        ]


class PublicProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    seller = SellerListSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    skus = PublicSKUSerializer(many=True, read_only=True)
    characteristics = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "description",
            "seller",
            "images",
            "characteristics",
            "category",
            "skus",
        ]