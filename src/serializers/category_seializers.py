from rest_framework import serializers
from src.models.product import (
    Category
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "value",
            "slug",
            "description",
            "image_url",
            "parent_id",
            "seo_title",
            "seo_description",
            "is_active",
            "created_at",
            "updated_at",
        ]