from django.contrib import admin, messages
from django.shortcuts import redirect
from .models.product import Invoice, InvoiceItem
from .api.invoices.service.main import accept_invoice

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    fields = ['sku', 'quantity', 'accepted_quantity']
    readonly_fields = ['quantity']
    extra = 0

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    inlines = [InvoiceItemInline]
    list_display = ['id', 'seller', 'status']
    change_form_template = "admin/invoice_change_form.html"

    def response_change(self, request, obj):
        if "_accept_invoice" in request.POST:
            try:
                items_data = obj.items.all()
                
                accept_invoice(
                    id=obj.id,
                    items=items_data,
                    operator=request.user
                )
                
                self.message_user(request, "Накладная успешно обработана!")
                return redirect(request.path)
            except Exception as e:
                self.message_user(request, f"Ошибка: {e}", level=messages.ERROR)
                return redirect(request.path)
        
        return super().response_change(request, obj)