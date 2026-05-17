from rest_framework import serializers

from src.models.product import BlockingReason, Product, ProductFieldReport, ProductImage
from src.models.user import Seller
from src.serializers.category_seializers import CategorySerializer
from src.serializers.skus_serializers import PublicSKUSerializer, SKUSerializer
from src.validators.main import validate_characteristics


class BlockingReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockingReason
        fields = ["id", "reason"]
        
class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "url", "ordering"]


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


class ProductListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    skus = SKUSerializer(many=True, read_only=True)

    skus_count = serializers.SerializerMethodField()
    total_active_quantity = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "title", "status", "category", "images", "created_at"]

    def get_skus_count(self, obj):
        return len(obj.skus)

    def get_total_active_quantity(self, obj):
        return sum(list(map(lambda sku: sku.active_quantity, obj.skus)))


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


class CreateProductSerializer(serializers.ModelSerializer):
    category_id = serializers.UUIDField(source="category.id", read_only=True)
    seller_id = serializers.UUIDField(source="seller.id", read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    skus = PublicSKUSerializer(many=True, read_only=True)
    characteristics = serializers.JSONField(required=False, allow_null=True)
    blocking_reason_id = serializers.UUIDField(
        source="blocking_reason.id", read_only=True
    )

    class Meta:
        model = Product
        fields = [
            "id",
            "seller_id",
            "category_id",
            "title",
            "slug",
            "description",
            "status",
            "deleted",
            "blocking_reason_id",
            "moderator_comment",
            "blocked",
            "images",
            "characteristics",
            "skus",
            "created_at",
            "updated_at",
        ]
