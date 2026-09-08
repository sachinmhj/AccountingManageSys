from django.contrib import admin
from .models import (
    Contact, ProductCategory, Product, 
    Invoice, InvoiceItem, InvoiceAllocation, 
    CustomerPayment, PaymentAllocation,
    SalesReturn, SalesReturnItem, UserProfile,
    PurchaseBill, PurchaseBillItem, SupplierPayment,
    ExpenseCategory, Expense
)

admin.site.register(Contact)
admin.site.register(ProductCategory)
admin.site.register(Product)
admin.site.register(UserProfile)

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1

class InvoiceAllocationInline(admin.TabularInline):
    model = InvoiceAllocation
    extra = 0

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    inlines = [InvoiceItemInline, InvoiceAllocationInline]
    list_display = ('invoice_number', 'customer', 'date', 'total_amount', 'status')
    list_filter = ('status', 'date')
    search_fields = ('invoice_number', 'customer__name')

class PaymentAllocationInline(admin.TabularInline):
    model = PaymentAllocation
    extra = 1

@admin.register(CustomerPayment)
class CustomerPaymentAdmin(admin.ModelAdmin):
    inlines = [PaymentAllocationInline]
    list_display = ('payment_number', 'customer', 'amount', 'payment_date', 'status')
    list_filter = ('status', 'payment_method')
    search_fields = ('payment_number', 'customer__name')

class SalesReturnItemInline(admin.TabularInline):
    model = SalesReturnItem
    extra = 1

@admin.register(SalesReturn)
class SalesReturnAdmin(admin.ModelAdmin):
    inlines = [SalesReturnItemInline]
    list_display = ('return_number', 'customer', 'return_date', 'total_amount', 'status')
    list_filter = ('status', 'refund_method')
    search_fields = ('return_number', 'customer__name')

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
