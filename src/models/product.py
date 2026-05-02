from django.db import models
from uuid import uuid4
from django.conf import settings
from django.core.validators import MinValueValidator

from src.models.category import Category
from src.validators.main import validate_characteristics

class ProductStatus(models.TextChoices):
    ON_MODERATION = 'on_moderation', 'On moderation'
    ACCEPTED = 'accepted', 'Accepted'
    BLOCKED = 'blocked', 'Blocked'


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, null=True, blank=True)
    characteristics = models.JSONField(default=None, null=True, blank=True, validators=[validate_characteristics])
    status = models.CharField(
        max_length=20,
        choices=ProductStatus.choices,
        default=ProductStatus.ON_MODERATION,
    )
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        db_table = 'products'
    
class SKU(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='skus')
    name = models.CharField(max_length=255)
    price = models.IntegerField(validators=[MinValueValidator(0)])
    characteristics = models.JSONField(default=None, null=True, blank=True, validators=[validate_characteristics])
    active_quantity = models.IntegerField(validators=[MinValueValidator(0)])
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
        constraints = [
            models.UniqueConstraint(fields=['product', 'order'], name='unique_product_image_order')
        ]


class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    date = models.DateField(auto_now_add=True)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invoices')
    class Meta:
        db_table = 'invoices'

class InvoiceItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    class Meta:
        db_table = 'invoice_items'
