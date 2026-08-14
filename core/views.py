from django.views.generic import TemplateView, CreateView, View
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils import timezone
from .models import Product, ProductCategory, Contact, Invoice, InvoiceItem, PurchaseBill, PurchaseBillItem, Expense, ExpenseCategory, CustomerPayment, SupplierPayment
from .forms import ProductForm, ProductCategoryForm, ContactForm, ExpenseForm, ExpenseCategoryForm


class HomeView(TemplateView):
    template_name = "pages/home.html"


class SalesView(TemplateView):
    template_name = "pages/sales.html"


class CustomerView(TemplateView):
    template_name = "pages/sales/customers.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Customers"
        # Only show customers and both
        context["customers"] = Contact.objects.filter(contact_type__in=['Customer', 'Both'])
        context["new_modal_action"] = "openContactModal('customer')"
        return context


class CustomerAddView(CreateView):
    model = Contact
    form_class = ContactForm
    template_name = "pages/sales/customer_add.html"
    success_url = reverse_lazy("customers")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add New Customer"
        return context


# ==================== SALES ====================

class InvoiceView(TemplateView):
    template_name = "pages/sales/invoice.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Invoice"
        context["tabs"] = ["All", "Draft", "Unpaid", "Paid"]
        context["invoices"] = Invoice.objects.select_related('customer').order_by('-date')
        context["new_url"] = "invoice_add"
        return context


class InvoiceAddView(View):
    template_name = "pages/sales/invoice_add.html"

    def get(self, request):
        customers = Contact.objects.filter(contact_type__in=['Customer', 'Both'])
        products = Product.objects.all()
        today = timezone.now().date()
        context = {
            'customers': customers,
            'products': products,
            'today': today,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        customer_id = request.POST.get('customer')
        invoice_date = request.POST.get('invoice_date')
        due_date = request.POST.get('due_date') or None

        if not customer_id:
            customers = Contact.objects.filter(contact_type__in=['Customer', 'Both'])
            products = Product.objects.all()
            return render(request, self.template_name, {
                'error': 'Please select a valid customer.',
                'customers': customers,
                'products': products,
                'today': timezone.now().date(),
            })

        try:
            customer = Contact.objects.get(id=customer_id)
        except (Contact.DoesNotExist, ValueError):
            customers = Contact.objects.filter(contact_type__in=['Customer', 'Both'])
            products = Product.objects.all()
            return render(request, self.template_name, {
                'error': 'Please select a valid customer.',
                'customers': customers,
                'products': products,
                'today': timezone.now().date(),
            })

        invoice = Invoice.objects.create(
            customer=customer,
            date=invoice_date,
            due_date=due_date,
            status='Draft',
        )

        # Process line items: product_id[], quantity[], unit_price[]
        product_ids = request.POST.getlist('product_id[]')
        quantities = request.POST.getlist('quantity[]')
        unit_prices = request.POST.getlist('unit_price[]')

        subtotal = 0
        for pid, qty, price in zip(product_ids, quantities, unit_prices):
            if pid and qty and price:
                try:
                    product = Product.objects.get(id=pid)
                    qty = int(qty)
                    price = float(price)
                    item_total = qty * price
                    subtotal += item_total
                    InvoiceItem.objects.create(
                        invoice=invoice,
                        product=product,
                        quantity=qty,
                        unit_price=price,
                        total_price=item_total,
                    )
                except (Product.DoesNotExist, ValueError):
                    pass

        # VAT 13%
        vat = round(subtotal * 0.13, 2)
        total = round(subtotal + vat, 2)
        invoice.subtotal = subtotal
        invoice.vat_amount = vat
        invoice.total_amount = total
        invoice.save()

        return redirect('invoice')

class CustomersView(TemplateView):
    template_name = "pages/sales/customers.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Customers"
        context["tabs"] = ["Customer", "Draft"]  # Added Draft tab
        context["approved_customers"] = []  # Pass your approved customers here
        context["draft_customers"] = []     # Pass your draft customers here
        context["new_action"] = "openCustomerModal()"
        return context



class CustomerPaymentView(TemplateView):
    template_name = "pages/sales/customer_payment.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Customer Payments"
        context["payments"] = CustomerPayment.objects.select_related('invoice__customer').order_by('-payment_date')
        context["new_url"] = "customer_payment_add"
        return context

class CustomerPaymentAddView(View):
    template_name = "pages/sales/customer_payment_add.html"

    def get(self, request):
        customers = Contact.objects.filter(contact_type__in=['Customer', 'Both'])
        context = {
            'title': "New Customer Payment",
            'customers': customers,
            'today': timezone.now().date(),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        customer_id = request.POST.get('customer')
        invoice_id = request.POST.get('invoice_id')
        amount_str = request.POST.get('amount')
        payment_date = request.POST.get('payment_date')
        payment_method = request.POST.get('payment_method')

        if not all([customer_id, invoice_id, amount_str, payment_date, payment_method]):
            return redirect('customer_payment_add')
        
        try:
            amount = float(amount_str)
            invoice = Invoice.objects.get(id=invoice_id, customer_id=customer_id)
        except (ValueError, Invoice.DoesNotExist):
            return redirect('customer_payment_add')

        # Enforce that payment cannot exceed total amount
        pending_amount = float(invoice.total_amount - invoice.paid_amount)
        if amount > pending_amount:
            amount = pending_amount

        if amount > 0:
            CustomerPayment.objects.create(
                invoice=invoice,
                amount=amount,
                payment_date=payment_date,
                payment_method=payment_method
            )
            
            # Update invoice
            invoice.paid_amount += amount
            if invoice.paid_amount >= invoice.total_amount:
                invoice.status = 'Paid'
            elif invoice.paid_amount > 0:
                invoice.status = 'Partially Paid'
            invoice.save()

        return redirect('customer_payment')

class UnpaidInvoicesJsonView(View):
    def get(self, request, customer_id):
        invoices = Invoice.objects.filter(
            customer_id=customer_id,
            status__in=['Draft', 'Unpaid', 'Partially Paid']
        )
        data = []
        for inv in invoices:
            pending = inv.total_amount - inv.paid_amount
            if pending > 0:
                data.append({
                    'id': inv.id,
                    'date': inv.date.isoformat(),
                    'total_amount': str(inv.total_amount),
                    'paid_amount': str(inv.paid_amount),
                    'pending_amount': str(pending),
                })
        return JsonResponse({'invoices': data})


# ==================== INVENTORY ====================

class InventoryView(TemplateView):
    template_name = "pages/inventory/inventory.html"


class InventoryProductView(TemplateView):
    template_name = "pages/inventory/inventory_product.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Products"
        context["tabs"] = ["Goods", "Services"]
        context["products"] = []
        return context


class VariantProductView(TemplateView):
    template_name = "pages/inventory/variant_product.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Variant Products"
        context["tabs"] = ["Products", "Services"]
        context["products"] = []
        context["new_url"] = "variant_product_add"
        return context
    
class VariantProductAddView(TemplateView):
    template_name = "pages/inventory/variant_product_add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "New Variant Product"
        return context


class VariantAttributeView(TemplateView):
    template_name = "pages/inventory/variant_attribute.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Variant Attributes"
        context["attributes"] = []
        context["new_action"]="openAttributeModal()"
        return context


class ProductCategoryView(TemplateView):
    template_name = "pages/inventory/product_category.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Product Categories"
        context["categories"] = []
        return context


class WarehouseTransferView(TemplateView):
    template_name = "pages/inventory/warehouse_transfer.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Warehouse Transfer"
        context["tabs"] = ["Approved", "Draft"]
        context["transfers"] = []
        context["new_url"] = "warehouse_add"
        return context
class WarehouseAddView(TemplateView):
    template_name = "pages/inventory/warehouse_add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "New Warehouse Transfer"
        return context


class InventoryAdjustmentView(TemplateView):
    template_name = "pages/inventory/inventory_adjust.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Inventory Adjustment"
        context["tabs"] = ["Approved", "Draft"]
        context["adjusts"] = []
        context["new_url"] = "inventory_adjust_add"       
        return context
class InventoryAdjustAddView(TemplateView):
    template_name = "pages/inventory/inventory_adjust_add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "New Inventory Adjustment"
        return context


class BillMaterialView(TemplateView):
    template_name = "pages/inventory/bills_material.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Bill of Materials"
        context["bills"] = []
        context["new_url"] = "bill_material_add"       
        return context
class BillMaterialAddView(TemplateView):
    template_name = "pages/inventory/bill_material_add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add New Bills Of Material"
        return context


class ProductionOrderView(TemplateView):
    template_name = "pages/inventory/production_order.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Production Order"
        context["tabs"] = ["Approved", "Draft"]
        context["orders"] = []
        context["new_url"] = "production_order_add"
        return context
class ProductionOrderAddView(TemplateView):
    template_name = "pages/inventory/production_order_add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add New Production Order"
        return context


class ProductionJournalView(TemplateView):
    template_name = "pages/inventory/production_journal.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Production Journal"
        context["tabs"] = ["Approved", "Draft"]
        context["journals"] = []
        context["new_url"]="production_journal_add"
        return context
class ProductionJournalAddView(TemplateView):
    template_name="pages/inventory/production_journal_add.html"
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        context["title"]="Add New Production Journal"
        return context 


# ==================== PURCHASE ====================

class PurchaseView(TemplateView):
    template_name = "pages/purchase/purchase.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Purchase Bills"
        context["tabs"] = ["All", "Draft", "Unpaid", "Paid"]
        context["purchases"] = PurchaseBill.objects.select_related('supplier').order_by('-date')
        context["new_url"] = "purchase_add"
        return context

class PurchaseAddView(View):
    template_name = "pages/purchase/purchase_add.html"

    def get(self, request):
        suppliers = Contact.objects.filter(contact_type__in=['Supplier', 'Both'])
        products = Product.objects.all()
        today = timezone.now().date()
        context = {
            'suppliers': suppliers,
            'products': products,
            'today': today,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        supplier_id = request.POST.get('supplier')
        bill_date = request.POST.get('bill_date')
        due_date = request.POST.get('due_date') or None

        if not supplier_id:
            return redirect('purchase_add')

        try:
            supplier = Contact.objects.get(id=supplier_id)
        except (Contact.DoesNotExist, ValueError):
            return redirect('purchase_add')

        bill = PurchaseBill.objects.create(
            supplier=supplier,
            date=bill_date,
            due_date=due_date,
            status='Draft',
        )

        product_ids = request.POST.getlist('product_id[]')
        quantities = request.POST.getlist('quantity[]')
        unit_prices = request.POST.getlist('unit_price[]')

        subtotal = 0
        for pid, qty, price in zip(product_ids, quantities, unit_prices):
            if pid and qty and price:
                try:
                    product = Product.objects.get(id=pid)
                    qty = int(qty)
                    price = float(price)
                    item_total = qty * price
                    subtotal += item_total
                    PurchaseBillItem.objects.create(
                        purchase_bill=bill,
                        product=product,
                        quantity=qty,
                        unit_price=price,
                        total_price=item_total,
                    )
                except (Product.DoesNotExist, ValueError):
                    pass

        vat = round(subtotal * 0.13, 2)
        total = round(subtotal + vat, 2)
        bill.subtotal = subtotal
        bill.vat_amount = vat
        bill.total_amount = total
        bill.save()

        return redirect('purchase')
    

class ExpensesView(TemplateView):
    template_name = "pages/purchase/expenses.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Expenses"
        context["expenses"] = Expense.objects.select_related('category').order_by('-date')
        context["new_url"] = "expenses_add"
        return context

class ExpensesAddView(CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = "pages/purchase/expenses_add.html"
    success_url = reverse_lazy("expenses")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add New Expense"
        return context



class SupplierPaymentView(TemplateView):
    template_name = "pages/purchase/supplier_payment.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Supplier Payments"
        context["payments"] = SupplierPayment.objects.select_related('purchase_bill__supplier').order_by('-payment_date')
        context["new_url"] = "supplier_payment_add"
        return context

class SupplierPaymentAddView(View):
    template_name = "pages/purchase/supplier_payment_add.html"

    def get(self, request):
        suppliers = Contact.objects.filter(contact_type__in=['Supplier', 'Both'])
        context = {
            'title': "New Supplier Payment",
            'suppliers': suppliers,
            'today': timezone.now().date(),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        supplier_id = request.POST.get('supplier')
        bill_id = request.POST.get('bill_id')
        amount_str = request.POST.get('amount')
        payment_date = request.POST.get('payment_date')
        payment_method = request.POST.get('payment_method')

        if not all([supplier_id, bill_id, amount_str, payment_date, payment_method]):
            return redirect('supplier_payment_add')
        
        try:
            amount = float(amount_str)
            bill = PurchaseBill.objects.get(id=bill_id, supplier_id=supplier_id)
        except (ValueError, PurchaseBill.DoesNotExist):
            return redirect('supplier_payment_add')

        # Enforce that payment cannot exceed total amount
        pending_amount = float(bill.total_amount - bill.paid_amount)
        if amount > pending_amount:
            amount = pending_amount

        if amount > 0:
            SupplierPayment.objects.create(
                purchase_bill=bill,
                amount=amount,
                payment_date=payment_date,
                payment_method=payment_method
            )
            
            # Update bill
            bill.paid_amount += amount
            if bill.paid_amount >= bill.total_amount:
                bill.status = 'Paid'
            elif bill.paid_amount > 0:
                bill.status = 'Partially Paid'
            bill.save()

        return redirect('supplier_payment')

class UnpaidPurchaseBillsJsonView(View):
    def get(self, request, supplier_id):
        bills = PurchaseBill.objects.filter(
            supplier_id=supplier_id,
            status__in=['Draft', 'Unpaid', 'Partially Paid']
        )
        data = []
        for bill in bills:
            pending = bill.total_amount - bill.paid_amount
            if pending > 0:
                data.append({
                    'id': bill.id,
                    'date': bill.date.isoformat(),
                    'total_amount': str(bill.total_amount),
                    'paid_amount': str(bill.paid_amount),
                    'pending_amount': str(pending),
                })
        return JsonResponse({'bills': data})

class UnitsMeasurementView(TemplateView):
    template_name = "pages/inventory/units_measurement.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Units Of Measurement"
        context["categories"] = []
        context["new_action"]="openCreateUnitModal()"
        return context


class SupplierAddView(TemplateView):
    template_name ="pages/purchase/supplier_add.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "New Supplier"
        return context