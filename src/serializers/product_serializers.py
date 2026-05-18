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


# class ProductSerializer(serializers.ModelSerializer):
#     category = CategorySerializer(read_only=True)
#     seller = SellerListSerializer(read_only=True)
#     images = ProductImageSerializer(many=True, read_only=True)
#     skus = SKUSerializer(many=True, read_only=True)
#     characteristics = serializers.JSONField(
#         required=False, allow_null=True, validators=[validate_characteristics]
#     )
#     field_reports = ProductFieldReportSerializer(many=True, read_only=True)

#     class Meta:
#         model = Product
#         fields = [
#             "id",
#             "title",
#             "description",
#             "status",
#             "blocking_reason",
#             "field_reports",
#             "seller",
#             "images",
#             "characteristics",
#             "category",
#             "skus",
#         ]


class ProductListSerializer(serializers.ModelSerializer):
    category_id = serializers.UUIDField(source="category.id", read_only=True)
    min_price = serializers.SerializerMethodField()
    cover_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "status",
            "category_id",
            "deleted",
            "created_at",
            "min_price",
            "cover_image",
        ]

    def get_min_price(self, obj):
        if obj.skus.exists():
            prices = [sku.price for sku in obj.skus.all()]
            return min(prices)
        return 0

    def get_cover_image(self, obj):
        first_image = obj.images.first()
        if first_image:
            return ProductImageSerializer(first_image).data["url"]
        return None


class PublicCatalogProductSerializer(serializers.ModelSerializer):
    category_id = serializers.UUIDField(source="category.id", read_only=True)
    min_price = serializers.SerializerMethodField()
    cover_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "slug",
            "status",
            "category_id",
            "min_price",
            "cover_image",
            "created_at",
        ]

    def get_min_price(self, obj):
        if obj.skus.exists():
            prices = [sku.price for sku in obj.skus.all()]
            return min(prices)
        return 0

    def get_cover_image(self, obj):
        first_image = obj.images.first()
        if first_image:
            return ProductImageSerializer(first_image).data["url"]
        return None


class PublicProductSerializer(serializers.ModelSerializer):
    category_id = serializers.UUIDField(source="category.id", read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    skus = PublicSKUSerializer(many=True, read_only=True)
    characteristics = serializers.JSONField(required=False, allow_null=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "description",
            "status",
            "images",
            "characteristics",
            "category_id",
            "skus",
        ]


class ProductSerializer(serializers.ModelSerializer):
    category_id = serializers.UUIDField(source="category.id", read_only=True)
    seller_id = serializers.UUIDField(source="seller.id", read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    skus = SKUSerializer(many=True, read_only=True)
    characteristics = serializers.JSONField(required=False, allow_null=True)
    blocking_reason_id = serializers.SerializerMethodField()
    field_reports = ProductFieldReportSerializer(many=True, read_only=True)

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
            "field_reports",
            "moderator_comment",
            "blocked",
            "images",
            "characteristics",
            "skus",
            "created_at",
            "updated_at",
        ]

    def get_blocking_reason_id(self, obj):
        return obj.blocking_reason.id if obj.blocking_reason else None
