import datetime
from uuid import uuid4

from django.db import models


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField()
    slug = models.CharField(null=True)
    description = models.CharField(null=True, blank=True)
    image_url = models.CharField(null=True, blank=True)
    parent_id = models.UUIDField(null=True, blank=True)
    seo_title = models.CharField(null=True, blank=True)
    seo_description = models.CharField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=datetime.datetime(2026, 5, 2, 12, 00, tzinfo=datetime.timezone.utc))
    updated_at = models.DateTimeField(default=datetime.datetime(2026, 5, 2, 12, 00, tzinfo=datetime.timezone.utc))

    class Meta:
        db_table = 'categories'


class CategorySEOKeyword(models.Model):
    category_id = models.UUIDField()
    name = models.CharField()

    class Meta:
        db_table = 'categories_keywords'


class CategoryMetaTag(models.Model):
    category_id = models.UUIDField()
    tag = models.CharField()
    value = models.CharField()

    class Meta:
        db_table = 'categories_metatags'


class CategoryFilter(models.Model):
    category_id = models.UUIDField()
    slug = models.CharField()
    name = models.CharField()
    type = models.CharField()
    values = models.JSONField()

    class Meta:
        db_table = 'categories_filters'
