import uuid

from src.models import Category


def get_categories():
    try:
        categories = Category.objects.all().values("id", "parent_id", "value")
        return list(categories)
    except Exception as e:
        raise Exception(f"failed to get categories: {e}")


def get_category(id: uuid.UUID) -> Category:
    try:
        category = Category.objects.get(id=id)
        return category
    except Exception as e:
        raise Exception(f"failed to get category: {e}")
