from django.contrib import admin
from .models import (
    Contact, ProductCategory, Product, 
    Invoice, InvoiceItem, CustomerPayment,
    PurchaseBill, PurchaseBillItem, SupplierPayment,
    ExpenseCategory, Expense
)

admin.site.register(Contact)
admin.site.register(ProductCategory)
admin.site.register(Product)

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    inlines = [InvoiceItemInline]
    list_display = ('id', 'customer', 'date', 'total_amount', 'status')
    list_filter = ('status', 'date')
    search_fields = ('customer__name',)

admin.site.register(CustomerPayment)

class PurchaseBillItemInline(admin.TabularInline):
    model = PurchaseBillItem
    extra = 1

@admin.register(PurchaseBill)
class PurchaseBillAdmin(admin.ModelAdmin):
    inlines = [PurchaseBillItemInline]
    list_display = ('id', 'supplier', 'date', 'total_amount', 'status')
    list_filter = ('status', 'date')
    search_fields = ('supplier__name',)

admin.site.register(SupplierPayment)
admin.site.register(ExpenseCategory)
admin.site.register(Expense)
