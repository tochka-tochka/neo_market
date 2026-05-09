from django.core.validators import MinValueValidator
from rest_framework import serializers

from src.models import Category
from src.models.product import (
    SKU,
    Invoice,
    InvoiceItem,
    Product,
    ProductFieldReport,
    ProductImage,
    SKUImage,
)
from src.models.user import Seller
from src.validators.main import validate_characteristics


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "product", "url", "order", "created_at"]


class SKUImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKUImage
        fields = ["id", "sku", "url", "order", "created_at"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "value",
            "slug",
            "description",
            "image_url",
            "parent_id",
            "seo_title",
            "seo_description",
            "is_active",
            "created_at",
            "updated_at",
        ]


class ProductIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id"]


class SKUSerializer(serializers.ModelSerializer):
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
            "cost_price",
            "discount",
            "active_quantity",
            "images",
            "characteristics",
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


class InvoiceItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    sku = SKUSerializer(read_only=True)
    quantity = serializers.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        model = InvoiceItem
        fields = ["id", "product", "sku", "quantity"]


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True)

    class Meta:
        model = Invoice
        fields = ["id", "date", "items"]


class SellerSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    invoices = InvoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Seller
        fields = ["id", "username", "password", "products"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Seller
        fields = ("username", "password")

    def create(self, validated_data):
        seller = Seller.objects.create_user(
            username=validated_data["username"], password=validated_data["password"]
        )
        return seller
