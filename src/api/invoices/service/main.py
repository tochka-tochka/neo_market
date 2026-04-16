from src.models.product import Invoice, InvoiceItem, Product, SKU
from src.serializes import InvoiceSerializer
from django.db import transaction
from datetime import datetime
from uuid import UUID

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
        invoice = Invoice.objects.create(
            date=datetime.now(),
            seller=seller
        )
        for item in data['items']:
            product = Product.objects.get(id=item['product_id'])
            sku = SKU.objects.get(id=item['sku_id'])
            if sku.product != product:
                raise Exception("failed to create invoice: product's sku doesn't exist")

            InvoiceItem.objects.create(
                product=product,
                sku=sku,
                quantity=item['quantity'],
                invoice=invoice
            )
        return invoice.id
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
def accept_invoice(id, seller):
    try:
        invoice = Invoice.objects.get(id=id)
        if invoice.seller != seller:
            raise Exception("access denied")
        
        for item in invoice.items.all():
            sku = item.sku
            sku.active_quantity -= item.quantity
            if sku.active_quantity < 0:
                raise Exception("failed to accept invoice: invoice quantity greater than actual")
            sku.save()

        invoice.delete()
            
    except Exception as e:
        raise Exception(f"failed to accept invoice: {e}")