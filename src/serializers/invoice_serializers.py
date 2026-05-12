from rest_framework import serializers

from src.models.product import (
    InvoiceItem,
    Invoice
)
from src.serializers.skus_serializers import SKUSerializer
from src.serializers.product_serializers import ProductSerializer
from django.core.validators import MinValueValidator

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