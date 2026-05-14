from rest_framework import serializers

from src.models.product import (
    InvoiceItem,
    Invoice
)
from django.core.validators import MinValueValidator

class InvoiceItemSerializer(serializers.ModelSerializer):
    sku_id = serializers.UUIDField(source='sku.id', read_only=True)
    sku_name = serializers.UUIDField(source='sku.name', read_only=True)
    quantity = serializers.IntegerField(validators=[MinValueValidator(1)])
    accepted_quantity = serializers.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        model = InvoiceItem
        fields = ["id", "sku_id", "sku_name", "quantity", "accepted_quantity"]


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True)

    class Meta:
        model = Invoice
        fields = ["id", "status", "created_at", "items"]