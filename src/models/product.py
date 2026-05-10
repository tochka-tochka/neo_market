from datetime import datetime
from django.db import models
from uuid import uuid4
from django.conf import settings
from django.core.validators import MinValueValidator

from src.models.category import Category
from src.validators.main import validate_characteristics

class ProductStatus(models.TextChoices):
    CREATED = 'CREATED'
    ON_MODERATION = 'ON_MODERATION'
    MODERATED = 'MODERATED'
    BLOCKED = 'BLOCKED'
    HARD_BLOCKED = 'HARD_BLOCKED'


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING, null=True, blank=True)
    characteristics = models.JSONField(default=None, null=True, blank=True, validators=[validate_characteristics])
    status = models.CharField(
        max_length=20,
        choices=ProductStatus.choices,
        default=ProductStatus.CREATED,
    )
    blocking_reason = models.TextField(null=True, blank=True)
    deleted = models.BooleanField(default=False)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True, null=True, blank=True,)

    class Meta:
        db_table = 'products'
    
class SKU(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, name="product", related_name='skus')
    name = models.CharField(max_length=255)
    price = models.IntegerField(validators=[MinValueValidator(0)])
    cost_price = models.IntegerField(validators=[MinValueValidator(0)])
    discount = models.IntegerField(default=0, null=True, blank=True, validators=[MinValueValidator(0)])
    characteristics = models.JSONField(default=None, null=True, blank=True, validators=[validate_characteristics])
    active_quantity = models.IntegerField(validators=[MinValueValidator(0)])
    reserved_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    class Meta:
        db_table = 'skus'

class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    url = models.ImageField(upload_to='products/')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_images'
        ordering = ['order', 'created_at']
        constraints = [
            models.UniqueConstraint(fields=['product', 'order'], name='unique_product_image_order')
        ]

class SKUImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    sku = models.ForeignKey(SKU, db_column='sku_id', on_delete=models.CASCADE, related_name='images')
    url = models.ImageField(upload_to='products/')
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sku_images'
        ordering = ['order', 'created_at']
        constraints = [
            models.UniqueConstraint(fields=['sku', 'order'], name='unique_sku_image_order')
        ]

class ProductFieldReport(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, name="product", related_name="field_reports")
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE, name="sku", related_name="sku_field_reports", blank=True, null=True)
    field = models.CharField(max_length=255)
    comment = models.CharField(max_length=255)


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

class ReserveOperations(models.Model):
    idempotency_key = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    result = models.JSONField(default=None, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'reserve_operations'

class ModerationDecisions(models.Model):
    idempotency_key = models.UUIDField(primary_key=True, default=uuid4, editable=False)