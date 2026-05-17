from django.core.validators import MinValueValidator
from rest_framework import serializers

from src.models.product import Invoice, InvoiceItem


class InvoiceItemSerializer(serializers.ModelSerializer):
    sku_id = serializers.UUIDField(source="sku.id", read_only=True)
    quantity = serializers.IntegerField(validators=[MinValueValidator(1)])
    accepted_quantity = serializers.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        model = InvoiceItem
        fields = ["id", "sku_id", "quantity", "accepted_quantity"]


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True)
    seller_id = serializers.UUIDField(source="seller.id", read_only=True)
    accepted_by = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            "id",
            "seller_id",
            "status",
            "items",
            "created_at",
            "updated_at",
            "accepted_at",
            "accepted_by",
        ]

    def get_accepted_by(self, obj):
        return obj.accepted_by.id if obj.accepted_by else None