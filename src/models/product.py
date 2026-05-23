from django.db.models import CASCADE, SET_NULL
from src.models.user import Seller
from datetime import datetime
from uuid import uuid4

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from src.models.category import Category
from src.validators.main import validate_characteristics


class ProductStatus(models.TextChoices):
    CREATED = "CREATED"
    ON_MODERATION = "ON_MODERATION"
    MODERATED = "MODERATED"
    BLOCKED = "BLOCKED"
    HARD_BLOCKED = "HARD_BLOCKED"


class BlockingReason(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=255)
    comment = models.TextField()

    class Meta:
        db_table = "blocking_reasons"


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    slug = models.CharField(max_length=255, default="", null=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.DO_NOTHING, null=True, blank=True
    )
    characteristics = models.JSONField(
        default=None, null=True, blank=True, validators=[validate_characteristics]
    )
    status = models.CharField(
        max_length=20,
        choices=ProductStatus.choices,
        default=ProductStatus.CREATED,
    )
    blocking_reason = models.ForeignKey(
        BlockingReason, on_delete=models.SET_NULL, null=True, blank=True
    )
    moderator_comment = models.TextField(default="", null=True, blank=True)
    deleted = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "products"


class SKU(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, name="product", related_name="skus"
    )
    name = models.CharField(max_length=255)
    price = models.IntegerField(validators=[MinValueValidator(0)])
    cost_price = models.IntegerField(validators=[MinValueValidator(0)])
    article = models.CharField(max_length=255)
    discount = models.IntegerField(
        default=0, null=True, blank=True, validators=[MinValueValidator(0)]
    )
    characteristics = models.JSONField(
        default=None, null=True, blank=True, validators=[validate_characteristics]
    )
    stock_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    active_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    reserved_quantity = models.IntegerField(
        default=0, validators=[MinValueValidator(0)]
    )
    updated_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "skus"


class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    url = models.ImageField()
    ordering = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "product_images"
        ordering = ["ordering"]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "ordering"], name="unique_product_image_order"
            )
        ]


class SKUImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    sku = models.ForeignKey(
        SKU, db_column="sku_id", on_delete=models.CASCADE, related_name="images"
    )
    url = models.ImageField()
    ordering = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "sku_images"
        ordering = ["ordering"]
        constraints = [
            models.UniqueConstraint(
                fields=["sku", "ordering"], name="unique_sku_image_order"
            )
        ]


class ProductFieldReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False) 
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, name="product", related_name="field_reports"
    )
    sku = models.ForeignKey(
        SKU,
        on_delete=models.CASCADE,
        name="sku",
        related_name="sku_field_reports",
        blank=True,
        null=True,
    )
    field_name = models.CharField(max_length=255)
    comment = models.CharField(max_length=255)

    class Meta:
        db_table = "product_field_reports"


class InvoiceStatus(models.TextChoices):
    CREATED = "CREATED"
    ACCEPTED = "ACCEPTED"
    PARTIALLY_ACCEPTED = "PARTIALLY_ACCEPTED"
    REJECTED = "REJECTED"


class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    status = models.TextField(
        choices=InvoiceStatus.choices, default=InvoiceStatus.CREATED
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    accepted_by = models.ForeignKey(
        Seller,
        on_delete=models.DO_NOTHING,
        related_name="accepted_invoices",
        null=True,
        blank=True,
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, related_name="invoices"
    )

    class Meta:
        db_table = "invoices"


class InvoiceItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    sku = models.ForeignKey(SKU, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    accepted_quantity = models.IntegerField(
        null=True, blank=True, validators=[MinValueValidator(0)]
    )
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")

    class Meta:
        db_table = "invoice_items"


class ReserveOperations(models.Model):
    idempotency_key = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    result = models.JSONField(default=None, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "reserve_operations"

class ModerationDecisions(models.Model):
    idempotency_key = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    class Meta:
        db_table = "moderation_decisions"

class OrderStatus(models.TextChoices):
    RESERVED = "RESERVED"
    UNRESERVED = "UNRESERVED"
    FULLIFIED = "FULLIFIED"

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    status = models.TextField(choices=OrderStatus.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    fullified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "orders"

class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=CASCADE, related_name="items")
    sku = models.ForeignKey(SKU, on_delete=SET_NULL, null=True)
    quantity = models.IntegerField(validators=[MinValueValidator(0)])

    class Meta:
        db_table = "order_items"