from src.models.product import Product, Category, Characteristic
from rest_framework import serializers

class CategorySerializer(serializers.ModelSerializer):
        class Meta:
            model = Category
            fields = ['id', 'value']

class CharacteristicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Characteristic
        fields = ['id', 'name', 'value']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    characteristics = CharacteristicSerializer( many=True, read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'status', 'image', 'category', 'characteristics']