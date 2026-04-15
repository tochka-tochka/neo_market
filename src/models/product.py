from django.db import models
from uuid import uuid4
from django.conf import settings

class ProductStatus(models.TextChoices):
    CREATED = 'active', 'Active'
    ON_MODERATION = 'on_moderation', 'On moderation'
    ACCEPTED = 'accepted', 'Accepted'
    BLOCKED = 'blocked', 'Blocked'

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    value = models.CharField(max_length=255)

    class Meta:
        db_table = 'categories'

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, default=None)
    characteristics = models.JSONField(default=None, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=ProductStatus.choices,
        default=ProductStatus.CREATED,
    )
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        db_table = 'products'
    
class SKU(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='skus')
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    characteristics = models.JSONField(default=None, null=True, blank=True)
    active_quantity = models.IntegerField()
    image = models.ImageField(upload_to='skus/', null=True, blank=True)

    class Meta:
        db_table = 'skus'

class Image(models.Model):
    """Модель для хранения изображений товара"""
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    url = models.ImageField(upload_to='products/')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'images'
        ordering = ['order', 'created_at']


class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    date = models.DateField()

class InvoiceItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
