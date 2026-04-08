from src.models.product import Product, Category, SKU, Image
from src.models.user import Seller
from rest_framework import serializers

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'product', 'url', 'order', 'created_at']

class CategorySerializer(serializers.ModelSerializer):
        class Meta:
            model = Category
            fields = ['id', 'value']

class SKUSerializer(serializers.ModelSerializer):

    images = ImageSerializer(many=True, read_only=True)

    class Meta:
        model = SKU
        fields = ['id', 'name', 'price', 'active_quantity', 'characteristics', 'image']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    images = ImageSerializer(many=True, read_only=True)
    
    skus = SKUSerializer(many=True, read_only=True)

    characteristics = serializers.JSONField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'status', 'images', 'characteristics', 'category', 'skus']

class ProductCreateSerializer(serializers.ModelSerializer):
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
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
                image=image, 
                order=index,
            )
        return product

class SellerSerializer(serializers.ModelSerializer):

    products = ProductSerializer(many=True, read_only=True)

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