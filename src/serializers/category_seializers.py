from rest_framework import serializers
from src.models.product import (
    Category
)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = [
            "id",
            "name",
            "parent_id",
        ]