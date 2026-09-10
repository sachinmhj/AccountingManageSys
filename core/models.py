from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


# ============================================================
# 1. Contacts (Customers & Suppliers)
# ============================================================

class Contact(models.Model):
    CONTACT_TYPES = (
        ('Customer', 'Customer'),
        ('Supplier', 'Supplier'),
        ('Both', 'Both'),
    )
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    phone_alt = models.CharField("Alt. Phone", max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    pan_vat_number = models.CharField("PAN/VAT Number", max_length=50, blank=True, null=True)
    vat_registered = models.BooleanField("VAT Registered", default=False)
    contact_type = models.CharField(max_length=10, choices=CONTACT_TYPES, default='Customer')

    # Financial defaults for this customer
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    # Meta
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def outstanding_balance(self):
        """Total unpaid amount across all invoices."""
        from django.db.models import Sum
        total = self.invoice_set.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        paid = self.invoice_set.aggregate(
            paid=Sum('paid_amount')
        )['paid'] or 0
        return (total - paid) + self.opening_balance

class ContactPerson(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name='persons')
    name = models.CharField(max_length=255)
    designation = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.designation}) - {self.contact.name}"


# ============================================================
# 2. Products & Inventory
# ============================================================

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
    UNIT_CHOICES = (
        ('Pcs', 'Pcs'),
        ('Kg', 'Kg'),
        ('Ltr', 'Ltr'),
        ('Box', 'Box'),
        ('Doz', 'Dozen'),
        ('Mtr', 'Meter'),
        ('Set', 'Set'),
        ('Pair', 'Pair'),
        ('Other', 'Other'),
    )
    code = models.CharField("Item Code", max_length=50, blank=True, null=True, unique=True)
    name = models.CharField(max_length=255)
    hs_code = models.CharField("HS Code", max_length=20, blank=True, null=True, help_text="Harmonized System Code for customs/tax classification")
    product_type = models.CharField(max_length=10, choices=PRODUCT_TYPES, default='Goods')
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True, blank=True)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='Pcs')
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    selling_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.code} - {self.name}" if self.code else self.name


# ============================================================
# 3. Sales — Invoice
# ============================================================

def generate_invoice_number():
    """Auto-generate invoice number like INV-000001."""
    last = Invoice.objects.order_by('-id').first()
    next_id = (last.id + 1) if last else 1
    return f"INV-{next_id:06d}"


class Invoice(models.Model):
    STATUS_CHOICES = (
        ('Draft', 'Draft'),
        ('Unpaid', 'Unpaid'),
        ('Partially Paid', 'Partially Paid'),
        ('Paid', 'Paid'),
    )
    SALES_TYPE_CHOICES = (
        ('Goods', 'Goods'),
        ('Services', 'Services'),
        ('Mixed', 'Mixed'),
    )
    SALE_CATEGORY_CHOICES = (
        ('Local Sales', 'Local Sales'),
        ('Export', 'Export'),
        ('Government', 'Government'),
    )
    VAT_TREATMENT_CHOICES = (
        ('Standard', 'Standard (13%)'),
        ('Zero Rated', 'Zero Rated (0%)'),
        ('Exempt', 'Exempt (No VAT)'),
    )
    CURRENCY_CHOICES = (
        ('NPR', 'NPR'),
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('INR', 'INR'),
    )
    PAYMENT_TERMS_CHOICES = (
        ('Immediate', 'Immediate'),
        ('15 Days', '15 Days'),
        ('30 Days', '30 Days'),
        ('45 Days', '45 Days'),
        ('60 Days', '60 Days'),
        ('90 Days', '90 Days'),
    )

    # Identification
    invoice_number = models.CharField(max_length=20, unique=True, editable=False)
    customer = models.ForeignKey(
        Contact, on_delete=models.CASCADE,
        limit_choices_to={'contact_type__in': ['Customer', 'Both']}
    )

    # Dates
    date = models.DateField(default=timezone.now)
    due_date = models.DateField(blank=True, null=True)
    payment_terms = models.CharField(max_length=20, choices=PAYMENT_TERMS_CHOICES, default='Immediate', blank=True)

    # Classification
    sales_type = models.CharField(max_length=20, choices=SALES_TYPE_CHOICES, default='Goods')
    sale_category = models.CharField(max_length=20, choices=SALE_CATEGORY_CHOICES, default='Local Sales')
    vat_treatment = models.CharField(max_length=20, choices=VAT_TREATMENT_CHOICES, default='Standard')
    currency = models.CharField(max_length=5, choices=CURRENCY_CHOICES, default='NPR')

    # Financial Fields
    subtotal_taxable = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    subtotal_non_taxable = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    taxable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    vat_amount = models.DecimalField("VAT Amount", max_digits=12, decimal_places=2, default=0.00)
    other_charges = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    round_off = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    # Internal Tracking (hidden from customer)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    gross_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    margin_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    # Payment Fields
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')

    # Notes & Misc
    terms_conditions = models.TextField(blank=True, null=True, default="Thank you for your business.")
    notes = models.TextField(blank=True, null=True)
    bill_attachment = models.FileField(upload_to='invoices/attachments/', blank=True, null=True)

    # Audit
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            # Temporary save to get ID, then set number
            super().save(*args, **kwargs)
            self.invoice_number = f"INV-{self.id:06d}"
            kwargs['force_insert'] = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_number} - {self.customer.name}"

    @property
    def balance_due(self):
        return self.total_amount - self.paid_amount


# ============================================================
# 4. Sales — Invoice Items
# ============================================================

class InvoiceItem(models.Model):
    DISCOUNT_TYPES = (
        ('Fixed', 'Fixed'),
        ('Percentage', 'Percentage'),
    )
    TAX_TYPE_CHOICES = (
        ('Standard', 'Standard (13%)'),
        ('Zero Rated', 'Zero Rated (0%)'),
        ('Exempt', 'Exempt (No VAT)'),
    )

    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    # Item details
    item_code = models.CharField(max_length=50, blank=True, null=True)
    hs_code = models.CharField("HS Code", max_length=20, blank=True, null=True)
    description = models.CharField(max_length=500, blank=True, null=True)
    unit = models.CharField(max_length=20, default='Pcs')

    # Quantity — negative means return
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    is_return = models.BooleanField(default=False)

    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    # Discount & Tax
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPES, default='Fixed')
    discount_value = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tax_type = models.CharField(max_length=20, choices=TAX_TYPE_CHOICES, default='Standard')
    taxable_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    vat_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=13.00)
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    # Internal Tracking
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    gross_profit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        prefix = "[RTN]" if self.is_return else ""
        return f"{prefix} {self.quantity} x {self.product.name} ({self.invoice.invoice_number})"


# ============================================================
# 5. Sales — Allocations (Profit/Commission Sharing)
# ============================================================

class InvoiceAllocation(models.Model):
    BASIS_CHOICES = (
        ('Percentage', 'Percentage'),
        ('Fixed', 'Fixed'),
    )
    invoice = models.ForeignKey(Invoice, related_name='allocations', on_delete=models.CASCADE)
    party_name = models.CharField(max_length=255)
    role = models.CharField(max_length=50)  # e.g. Salesperson, Broker, Agent
    basis = models.CharField(max_length=20, choices=BASIS_CHOICES, default='Percentage')
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    allocated_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.party_name} ({self.role}) - {self.allocated_amount} on {self.invoice.invoice_number}"


# ============================================================
# 6. Customer Payments (Restructured — linked to Customer, not Invoice)
# ============================================================

class CustomerPayment(models.Model):
    PAYMENT_METHODS = (
        ('Cash', 'Cash'),
        ('Bank Transfer', 'Bank Transfer'),
        ('Cheque', 'Cheque'),
        ('Online', 'Online'),
        ('Mobile Banking', 'Mobile Banking'),
    )
    STATUS_CHOICES = (
        ('Unallocated', 'Unallocated'),
        ('Partially Allocated', 'Partially Allocated'),
        ('Fully Allocated', 'Fully Allocated'),
    )

    # Now linked to Customer, not a single invoice
    customer = models.ForeignKey(
        Contact, on_delete=models.CASCADE,
        limit_choices_to={'contact_type__in': ['Customer', 'Both']},
        related_name='payments'
    )
    # Optionally link to the invoice that triggered this payment
    invoice = models.ForeignKey(
        Invoice, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='triggered_payments',
        help_text="The new invoice this payment was received with (if any)"
    )

    payment_number = models.CharField(max_length=20, unique=True, editable=False)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='Cash')
    bank_account = models.CharField(max_length=100, blank=True, null=True)
    reference_no = models.CharField(max_length=100, blank=True, null=True)
    narration = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Unallocated')

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.payment_number:
            super().save(*args, **kwargs)
            self.payment_number = f"PAY-{self.id:06d}"
            kwargs['force_insert'] = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.payment_number} - {self.customer.name} - Rs. {self.amount}"

    @property
    def allocated_amount(self):
        from django.db.models import Sum
        return self.allocations.aggregate(total=Sum('amount'))['total'] or 0

    @property
    def unallocated_amount(self):
        return self.amount - self.allocated_amount


class PaymentAllocation(models.Model):
    """Links a single CustomerPayment to one or more Invoices."""
    payment = models.ForeignKey(CustomerPayment, related_name='allocations', on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoice, related_name='payment_allocations', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    allocated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.payment.payment_number} → {self.invoice.invoice_number}: Rs. {self.amount}"


# ============================================================
# 7. Sales Return
# ============================================================

def generate_return_number():
    last = SalesReturn.objects.order_by('-id').first()
    next_id = (last.id + 1) if last else 1
    return f"SR-{next_id:06d}"


class SalesReturn(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Adjusted', 'Adjusted'),
        ('Refunded', 'Refunded'),
    )
    REFUND_METHOD_CHOICES = (
        ('Adjust in Next Invoice', 'Adjust in Next Invoice'),
        ('Refund to Customer', 'Refund to Customer'),
        ('Credit Note', 'Credit Note'),
    )

    return_number = models.CharField(max_length=20, unique=True, editable=False)
    customer = models.ForeignKey(
        Contact, on_delete=models.CASCADE,
        limit_choices_to={'contact_type__in': ['Customer', 'Both']},
        related_name='sales_returns'
    )
    original_invoice = models.ForeignKey(
        Invoice, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='returns',
        help_text="The original sale this return is for"
    )

    return_date = models.DateField(default=timezone.now)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)

    # Financials
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    refund_method = models.CharField(max_length=30, choices=REFUND_METHOD_CHOICES, default='Adjust in Next Invoice')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    notes = models.TextField(blank=True, null=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.return_number:
            super().save(*args, **kwargs)
            self.return_number = f"SR-{self.id:06d}"
            kwargs['force_insert'] = False
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.return_number} - {self.customer.name}"


class SalesReturnItem(models.Model):
    TAX_TYPE_CHOICES = (
        ('Standard', 'Standard (13%)'),
        ('Zero Rated', 'Zero Rated (0%)'),
        ('Exempt', 'Exempt (No VAT)'),
    )

    sales_return = models.ForeignKey(SalesReturn, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    item_code = models.CharField(max_length=50, blank=True, null=True)
    unit = models.CharField(max_length=20, default='Pcs')
    returned_qty = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    rate = models.DecimalField(max_digits=12, decimal_places=2)
    tax_type = models.CharField(max_length=20, choices=TAX_TYPE_CHOICES, default='Standard')
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    # Added from client notes
    DISPOSITION_CHOICES = (
        ('Saleable', 'Saleable'),
        ('Damaged', 'Damaged'),
    )
    disposition = models.CharField(max_length=20, choices=DISPOSITION_CHOICES, default='Saleable')
    reason = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.returned_qty} x {self.product.name} (Return {self.sales_return.return_number})"


# ============================================================
# 8. Quotations / Sales Orders
# ============================================================

def generate_quotation_number():
    last = Quotation.objects.order_by('-id').first()
    next_id = (last.id + 1) if last else 1
    return f"QTN-{next_id:06d}"

class Quotation(models.Model):
    STATUS_CHOICES = (
        ('Draft', 'Draft'),
        ('Sent', 'Sent'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    )

    quotation_number = models.CharField(max_length=50, unique=True, default=generate_quotation_number)
    customer = models.ForeignKey(Contact, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    valid_until = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    
    currency = models.CharField(max_length=10, default="NPR")
    notes = models.TextField(blank=True, null=True)
    
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    round_off = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.quotation_number

class QuotationItem(models.Model):
    TAX_TYPE_CHOICES = (
        ('Standard', 'Standard (13%)'),
        ('Zero Rated', 'Zero Rated (0%)'),
        ('Exempt', 'Exempt (No VAT)'),
    )

    quotation = models.ForeignKey(Quotation, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    unit = models.CharField(max_length=20, default='Pcs')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    rate = models.DecimalField(max_digits=12, decimal_places=2)
    tax_type = models.CharField(max_length=20, choices=TAX_TYPE_CHOICES, default='Standard')
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"


# ============================================================
# 9. Purchases & Expenses
# ============================================================

class PurchaseBill(models.Model):
    STATUS_CHOICES = (
        ('Draft', 'Draft'),
        ('Unpaid', 'Unpaid'),
        ('Partially Paid', 'Partially Paid'),
        ('Paid', 'Paid'),
    )
    supplier = models.ForeignKey(
        Contact, on_delete=models.CASCADE,
        limit_choices_to={'contact_type__in': ['Supplier', 'Both']}
    )
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


# ============================================================
# 9. User Profile (Role-based Permissions)
# ============================================================

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    can_view_margins = models.BooleanField(default=False)
    can_view_cost = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} Profile"


# ============================================================
# 10. Document / Receipt Manager Inbox (Tigg-style)
# ============================================================

class ReceiptDocument(models.Model):
    LABEL_CHOICES = (
        ('UNLABELED', 'Add Label'),
        ('INVOICE', 'Sales Invoice'),
        ('PURCHASE', 'Purchase Bill'),
        ('EXPENSE', 'Expense'),
        ('PAYMENT', 'Payment'),
    )
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('DONE', 'Done'),
    )

    file = models.FileField(upload_to='documents/receipts/')
    original_name = models.CharField(max_length=255)
    file_size = models.FloatField("Size (MB)", default=0.0)
    description = models.TextField(blank=True, null=True)
    label = models.CharField(max_length=30, choices=LABEL_CHOICES, default='UNLABELED')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    linked_invoice = models.ForeignKey('Invoice', on_delete=models.SET_NULL, null=True, blank=True, related_name='linked_receipt_documents')

    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.original_name} ({self.status})"
