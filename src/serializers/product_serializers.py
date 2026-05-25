from rest_framework import serializers

from src.models.product import BlockingReason, Product, ProductFieldReport, ProductImage, ProductCharacteristics, \
    SkuCharacteristics
from src.models.user import Seller
from src.serializers.category_seializers import CategorySerializer
from src.serializers.skus_serializers import PublicSKUSerializer, SKUSerializer
from src.validators.main import validate_characteristics


class BlockingReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockingReason
        fields = ["id", "title", "comment"]


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ["id", "url", "ordering"]


class ProductFieldReportSerializer(serializers.ModelSerializer):
    sku_id = serializers.SerializerMethodField()

    class Meta:
        model = ProductFieldReport
        fields = ["sku_id", "field_name", "comment"]

    def get_sku_id(self, obj):
        return obj.sku.id if obj.sku else None


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


class ProductCharacteristicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCharacteristics
        fields = ["id", "product_id", "name", "value"]


class PublicProductSerializer(serializers.ModelSerializer):
    category_id = serializers.UUIDField(source="category.id", read_only=True)
    seller_id = serializers.UUIDField(source="seller.id", read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    skus = PublicSKUSerializer(many=True, read_only=True)
    characteristics = ProductCharacteristicSerializer(many=True, read_only=True)

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
            "images",
            "characteristics",
            "skus",
            "created_at",
            "updated_at"
        ]


class ProductSerializer(serializers.ModelSerializer):
    category_id = serializers.UUIDField(source="category.id", read_only=True)
    seller_id = serializers.UUIDField(source="seller.id", read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    skus = SKUSerializer(many=True, read_only=True)
    characteristics = ProductCharacteristicSerializer(many=True, read_only=True)
    blocking_reason = BlockingReasonSerializer(read_only=True)
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
            "blocking_reason",
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
