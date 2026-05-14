from datetime import datetime
from uuid import UUID

from django.db import transaction

from src.models.product import SKU, Invoice, InvoiceItem, Product, ProductStatus
from src.serializers.invoice_serializers import InvoiceSerializer


class ProductNotModerated(Exception):
    pass


class AccessDenied(Exception):
    pass


@transaction.atomic
def get_all_invoices(seller):
    try:
        invoices = Invoice.objects.filter(seller=seller)
        serializer = InvoiceSerializer(invoices, many=True)
        return serializer.data
    except Exception as e:
        raise Exception(f"failed to get invoices: {e}")


@transaction.atomic
def create_invoice(data, seller):
    try:
        invoice = Invoice.objects.create(created_at=datetime.now(), seller=seller)
        for item in data["items"]:
            sku = SKU.objects.get(id=item["sku_id"])
            product = Product.objects.get(id=sku.product.id)
            if product.status != ProductStatus.MODERATED:
                raise ProductNotModerated(
                    "Invoice can only be created for MODERATED products"
                )

            if product.seller != seller:
                raise AccessDenied(
                    "One or more SKUs do not belong to the authenticated seller"
                )

            invoice_item = InvoiceItem(
                sku=sku, quantity=item["quantity"], invoice=invoice
            )
            invoice_item.full_clean()
            invoice_item.save()
        return InvoiceSerializer(invoice).data
    except AccessDenied as e:
        raise e
    except ProductNotModerated as e:
        raise e
    except Exception as e:
        raise Exception(f"failed to create invoice: {e}")


@transaction.atomic
def delete_invoice(id, seller):
    try:
        invoice = Invoice.objects.get(id=id)
        if invoice.seller != seller:
            raise Exception("access denied")
        invoice.delete()
    except Exception as e:
        raise Exception(f"failed to delete invoice: {e}")


@transaction.atomic
def accept_invoice(id, items):
    try:
        invoice = Invoice.objects.get(id=id)

        status = "ACCEPTED"
        count_accepted = 0

        for item in items:
            if item.accepted_quantity > 0:
                count_accepted += item.accepted_quantity

            if item.quantity > item.accepted_quantity:
                status = "PARTIALLY_ACCEPTED"
            elif item.quantity < item.accepted_quantity:
                raise Exception(
                    "accepted quantity can't be greater than actual quantity"
                )

            sku = item.sku
            sku.active_quantity += item.accepted_quantity
            sku.save()

        if count_accepted == 0:
            status = "REJECTED"

        invoice.status = status
        invoice.save()

        return invoice
    except Exception as e:
        raise Exception(f"failed to accept invoice: {e}")
