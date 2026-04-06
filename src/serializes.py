from src.models.product import Product, Category, SKU
from src.models.user import Seller
from rest_framework import serializers

class CategorySerializer(serializers.ModelSerializer):
        class Meta:
            model = Category
            fields = ['id', 'value']

class SKUSerializer(serializers.ModelSerializer):
    class Meta:
        model = SKU
        fields = ['id', 'name', 'price', 'active_quantity', 'characteristics', 'image']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    
    skus = SKUSerializer(many=True, read_only=True)

    characteristics = serializers.JSONField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'status', 'image', 'characteristics', 'category', 'skus']

class SellerSerializer(serializers.ModelSerializer):

    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Seller
        fields = ['id', 'login', 'password']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Seller
        fields = ('username', 'password')

    def create(self, validated_data):
        # Используем create_user, чтобы пароль захешировался автоматически
        seller = Seller.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return seller