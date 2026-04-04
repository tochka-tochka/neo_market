from django.db import models
from uuid import uuid4

class ProductStatus(models.TextChoices):
    CREATED = 'created', 'Created'
    ON_MODERATION = 'on_moderation', 'On moderation'
    ACCEPTED = 'accepted', 'Accepted'
    BLOCKED = 'blocked', 'Blocked'

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=ProductStatus.choices,
        default=ProductStatus.CREATED,
    )
    image = models.URLField()

    class Meta:
        db_table = 'products'
    
class SKU(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='skus')
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    active_quantity = models.IntegerField()

    class Meta:
        db_table = 'skus'

class Characteristic(models.Model):
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE, related_name='characteristic')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='characteristic')
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    class Meta:
        db_table = 'characteristics'

class Category(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='categories')
    value = models.CharField(max_length=255)

    class Meta:
        db_table = 'categories'