from rest_framework import serializers
from src.serializers.product_serializers import ProductSerializer
from src.serializers.invoice_serializers import InvoiceSerializer

from src.models.user import Seller

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