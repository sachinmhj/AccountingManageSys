from django.db import models
from django.utils import timezone

# 1. Contacts (Customers & Suppliers)
class Contact(models.Model):
    CONTACT_TYPES = (
        ('Customer', 'Customer'),
        ('Supplier', 'Supplier'),
        ('Both', 'Both'),
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    pan_vat_number = models.CharField("PAN/VAT Number", max_length=50, blank=True, null=True)
    contact_type = models.CharField(max_length=10, choices=CONTACT_TYPES, default='Customer')

    def __str__(self):
        return self.name


# 2. Products & Inventory
class ProductCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Product Categories"

    def __str__(self):
        return self.name


class Product(models.Model):
    PRODUCT_TYPES = (
        ('Goods', 'Goods'),
        ('Service', 'Service'),
    )
    name = models.CharField(max_length=255)
    product_type = models.CharField(max_length=10, choices=PRODUCT_TYPES, default='Goods')
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# 3. Sales
class Invoice(models.Model):
    STATUS_CHOICES = (
        ('Draft', 'Draft'),
        ('Unpaid', 'Unpaid'),
        ('Partially Paid', 'Partially Paid'),
        ('Paid', 'Paid'),
    )
    customer = models.ForeignKey(Contact, on_delete=models.CASCADE, limit_choices_to={'contact_type__in': ['Customer', 'Both']})
    date = models.DateField(default=timezone.now)
    due_date = models.DateField(blank=True, null=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    vat_amount = models.DecimalField("VAT Amount", max_digits=12, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')

    def __str__(self):
        return f"Invoice #{self.id} - {self.customer.name}"


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Invoice #{self.invoice.id})"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class CustomerPayment(models.Model):
    PAYMENT_METHODS = (
        ('Cash', 'Cash'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Cheque', 'Cheque'),
        ('Online', 'Online'),
    )
    invoice = models.ForeignKey(Invoice, related_name='payments', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='Cash')

    def __str__(self):
        return f"Payment of {self.amount} for Invoice #{self.invoice.id}"


# 4. Purchases & Expenses
class PurchaseBill(models.Model):
    STATUS_CHOICES = (
        ('Draft', 'Draft'),
        ('Unpaid', 'Unpaid'),
        ('Partially Paid', 'Partially Paid'),
        ('Paid', 'Paid'),
    )
    supplier = models.ForeignKey(Contact, on_delete=models.CASCADE, limit_choices_to={'contact_type__in': ['Supplier', 'Both']})
    date = models.DateField(default=timezone.now)
    due_date = models.DateField(blank=True, null=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    vat_amount = models.DecimalField("VAT Amount", max_digits=12, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')

    def __str__(self):
        return f"Bill #{self.id} - {self.supplier.name}"


class PurchaseBillItem(models.Model):
    purchase_bill = models.ForeignKey(PurchaseBill, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Bill #{self.purchase_bill.id})"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)


class SupplierPayment(models.Model):
    PAYMENT_METHODS = (
        ('Cash', 'Cash'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Cheque', 'Cheque'),
        ('Online', 'Online'),
    )
    purchase_bill = models.ForeignKey(PurchaseBill, related_name='payments', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='Cash')

    def __str__(self):
        return f"Payment of {self.amount} for Bill #{self.purchase_bill.id}"


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name_plural = "Expense Categories"

    def __str__(self):
        return self.name


class Expense(models.Model):
    PAYMENT_METHODS = (
        ('Cash', 'Cash'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Cheque', 'Cheque'),
        ('Online', 'Online'),
    )
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(default=timezone.now)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='Cash')
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.category.name} - {self.amount} on {self.date}"
