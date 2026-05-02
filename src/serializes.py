from rest_framework import serializers
from django.core.validators import MinValueValidator
from src.models.product import Product, SKU, Image, InvoiceItem, Invoice
from src.models import Category
from src.models.user import Seller
from src.validators.main import validate_characteristics


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'product', 'url', 'order', 'created_at']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'value', 'slug', 'description',
                  'image_url', 'parent_id', 'seo_title', 'seo_description',
                  'is_active', 'created_at', 'updated_at']


class SKUSerializer(serializers.ModelSerializer):
    price = serializers.IntegerField(validators=[MinValueValidator(0)])
    active_quantity = serializers.IntegerField(validators=[MinValueValidator(0)])
    characteristics = serializers.JSONField(
        required=False, 
        allow_null=True, 
        validators=[validate_characteristics]
    )

    class Meta:
        model = SKU
        fields = ['id', 'name', 'price', 'active_quantity', 'characteristics']

class SellerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ['id', 'username']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    seller = SellerListSerializer(read_only=True)
    images = ImageSerializer(many=True, read_only=True)
    skus = SKUSerializer(many=True, read_only=True)
    characteristics = serializers.JSONField(
        required=False, 
        allow_null=True, 
        validators=[validate_characteristics]
    )

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'status', 'seller', 'images', 'characteristics', 'category', 'skus']


class ProductCreateSerializer(serializers.ModelSerializer):
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )
    characteristics = serializers.JSONField(
        required=False, 
        allow_null=True, 
        validators=[validate_characteristics]
    )
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True
    )

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'category', 'characteristics', 'seller', 'uploaded_images']

    def create(self, validated_data):
        images_data = validated_data.pop('uploaded_images', [])
        
        product = Product.objects.create(**validated_data)
        
        for index, image in enumerate(images_data):
            Image.objects.create(
                product=product, 
                url=image,  # ← Было 'image', должно быть 'url'
                order=index,
            )
        return product


class InvoiceItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    sku = SKUSerializer(read_only=True)
    quantity = serializers.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        model = InvoiceItem
        fields = ['id', 'product', 'sku', 'quantity']


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True)

    class Meta:
        model = Invoice
        fields = ['id', 'date', 'items']


class SellerSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    invoices = InvoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Seller
        fields = ['id', 'username', 'password', 'products']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Seller
        fields = ('username', 'password')

    def create(self, validated_data):
        seller = Seller.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return seller