from django.views.generic import TemplateView, CreateView, View
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.db.models import Sum, Count
from decimal import Decimal
from django.http import JsonResponse
from django.utils import timezone
from .models import (
    Product, ProductCategory, Contact, Invoice, InvoiceItem,
    InvoiceAllocation, PaymentAllocation, CustomerPayment,
    PurchaseBill, PurchaseBillItem, Expense, ExpenseCategory,
    SupplierPayment, SalesReturn, SalesReturnItem, UserProfile,
    ContactPerson, Quotation, QuotationItem
)
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
        context["customers"] = Contact.objects.filter(contact_type__in=['Customer', 'Both'])
        # Load recent invoices for first customer (default view)
        first_customer = Contact.objects.filter(contact_type__in=['Customer', 'Both']).first()
        if first_customer:
            context["recent_invoices"] = Invoice.objects.filter(customer=first_customer).order_by('-date')[:10]
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
        context["title"] = "Sales History"
        invoices = Invoice.objects.select_related('customer').order_by('-date')
        context["invoices"] = invoices
        context["customers"] = Contact.objects.filter(contact_type__in=['Customer', 'Both'])
        # Totals for summary cards
        totals = invoices.aggregate(
            total_sales=Sum('total_amount'),
            total_vat=Sum('vat_amount'),
            total_received=Sum('paid_amount'),
        )
        context["total_sales"] = totals['total_sales'] or Decimal('0.00')
        context["total_vat"] = totals['total_vat'] or Decimal('0.00')
        context["total_received"] = totals['total_received'] or Decimal('0.00')
        context["total_due"] = context["total_sales"] - context["total_received"]
        context["new_url"] = "invoice_add"
        return context


class InvoiceDetailView(View):
    template_name = "pages/sales/invoice_detail.html"

    def get(self, request, pk):
        invoice = get_object_or_404(
            Invoice.objects.select_related('customer', 'created_by'),
            pk=pk
        )
        items = invoice.items.select_related('product').all()
        payments = invoice.payment_allocations.select_related('payment').order_by('-payment__payment_date')
        returns = invoice.returns.all()

        # Customer snapshot: total sales, receivable, paid, overdue
        customer = invoice.customer
        cust_invoices = Invoice.objects.filter(customer=customer)
        snap_total_sales = cust_invoices.aggregate(t=Sum('total_amount'))['t'] or Decimal('0.00')
        snap_total_paid  = cust_invoices.aggregate(t=Sum('paid_amount'))['t']  or Decimal('0.00')
        snap_receivable  = snap_total_sales - snap_total_paid

        paid_pct = 0
        if invoice.total_amount > 0:
            paid_pct = int((invoice.paid_amount / invoice.total_amount) * 100)
            paid_pct = min(paid_pct, 100)

        context = {
            'invoice': invoice,
            'items': items,
            'payments': payments,
            'returns': returns,
            'paid_pct': paid_pct,
            'snap_total_sales': snap_total_sales,
            'snap_total_paid': snap_total_paid,
            'snap_receivable': snap_receivable,
            'snap_overdue': snap_receivable,
        }
        return render(request, self.template_name, context)


class CustomerPaymentDetailView(View):
    template_name = "pages/sales/customer_payment_detail.html"

    def get(self, request, pk):
        payment = get_object_or_404(CustomerPayment.objects.select_related('customer'), pk=pk)
        return render(request, self.template_name, {'payment': payment})


class SalesReturnDetailView(View):
    template_name = "pages/sales/sales_return_detail.html"

    def get(self, request, pk):
        sales_return = get_object_or_404(SalesReturn.objects.select_related('customer'), pk=pk)
        items = sales_return.items.select_related('product').all()
        return render(request, self.template_name, {'sales_return': sales_return, 'items': items})


class SalesReturnView(View):
    template_name = "pages/sales/invoice_return.html"

    def get(self, request):
        customers = Contact.objects.filter(contact_type__in=['Customer', 'Both']).order_by('name')
        products = Product.objects.all()
        invoices = Invoice.objects.select_related('customer').order_by('-date')[:50]
        recent_returns = SalesReturn.objects.select_related('customer', 'original_invoice').order_by('-return_date')[:10]
        product_list = list(products.values('id', 'name', 'code', 'selling_price', 'unit', 'purchase_price', 'description'))
        context = {
            'title': 'Sales Return',
            'customers': customers,
            'products': products,
            'invoices': invoices,
            'recent_returns': recent_returns,
            'products_json': json.dumps(product_list, cls=DjangoJSONEncoder),
            'today': timezone.now().date(),
        }
        return render(request, self.template_name, context)

    @transaction.atomic
    def post(self, request):
        customer_id = request.POST.get('customer')
        if not customer_id:
            return redirect('invoice_return')

        customer = get_object_or_404(Contact, id=customer_id)
        return_date = request.POST.get('return_date') or timezone.now().date()
        original_invoice_id = request.POST.get('original_invoice') or None
        contact_person = request.POST.get('contact_person', '')
        mobile = request.POST.get('mobile', '')
        refund_method = request.POST.get('refund_method', 'Adjust in Next Invoice')
        notes = request.POST.get('notes', '')

        original_invoice = None
        if original_invoice_id:
            original_invoice = Invoice.objects.filter(id=original_invoice_id).first()

        sales_return = SalesReturn.objects.create(
            customer=customer,
            original_invoice=original_invoice,
            return_date=return_date,
            contact_person=contact_person,
            mobile=mobile,
            refund_method=refund_method,
            notes=notes,
            status='Pending',
            created_by=request.user if request.user.is_authenticated else None
        )

        product_ids    = request.POST.getlist('product_id[]')
        returned_qtys  = request.POST.getlist('returned_qty[]')
        unit_prices    = request.POST.getlist('unit_price[]')
        tax_types      = request.POST.getlist('tax_type[]')
        units          = request.POST.getlist('unit[]')
        dispositions   = request.POST.getlist('disposition[]')

        subtotal = Decimal('0.00')
        total_vat = Decimal('0.00')

        for i in range(len(product_ids)):
            if not product_ids[i]:
                continue
            product = Product.objects.get(id=product_ids[i])
            qty = Decimal(returned_qtys[i]) if returned_qtys[i] else Decimal('0')
            rate = Decimal(unit_prices[i]) if unit_prices[i] else Decimal('0.00')
            tax_type = tax_types[i] if i < len(tax_types) else 'Taxable'
            unit = units[i] if i < len(units) else 'Pcs'
            disposition = dispositions[i] if i < len(dispositions) else 'Saleable'

            line_amount = qty * rate
            vat_pct = Decimal('13.00') if tax_type == 'Taxable' else Decimal('0.00')
            tax_amount = line_amount * (vat_pct / Decimal('100.0'))
            item_total = line_amount + tax_amount

            subtotal += line_amount
            total_vat += tax_amount

            SalesReturnItem.objects.create(
                sales_return=sales_return,
                product=product,
                item_code=product.code,
                unit=unit,
                returned_qty=qty,
                rate=rate,
                tax_type=tax_type,
                tax_amount=tax_amount,
                amount=item_total,
                disposition=disposition,
                reason=notes,
            )

        total_return = subtotal + total_vat
        sales_return.subtotal = subtotal
        sales_return.vat_amount = total_vat
        sales_return.total_amount = total_return
        sales_return.save()

        # ── Apply Refund Method to customer balance ──────────────────────────
        if refund_method == 'Adjust in Next Invoice':
            remaining_credit = total_return
            
            # 1. Auto-allocate against unpaid invoices (oldest first)
            unpaid_invoices = Invoice.objects.filter(
                customer=customer, 
                status__in=['Draft', 'Unpaid', 'Partially Paid']
            ).order_by('date', 'id')
            
            for inv in unpaid_invoices:
                if remaining_credit <= 0:
                    break
                    
                pending_amount = inv.total_amount - inv.paid_amount
                if pending_amount > 0:
                    allocate_amount = min(remaining_credit, pending_amount)
                    
                    # Create a payment record for this invoice
                    CustomerPayment.objects.create(
                        customer=customer,
                        invoice=inv,
                        amount=allocate_amount,
                        payment_date=return_date,
                        payment_method='Adjusted Return',
                        narration=f'Auto-adjusted from Return {sales_return.return_number}',
                        created_by=request.user if request.user.is_authenticated else None,
                    )
                    
                    # Update invoice
                    inv.paid_amount += allocate_amount
                    if inv.paid_amount >= inv.total_amount:
                        inv.status = 'Paid'
                    else:
                        inv.status = 'Partially Paid'
                    inv.save()
                    
                    remaining_credit -= allocate_amount
            
            # 2. If there's STILL credit left, reduce their opening balance (store credit)
            if remaining_credit > 0:
                Contact.objects.filter(pk=customer.pk).update(
                    opening_balance=customer.opening_balance - remaining_credit
                )
                
            sales_return.status = 'Adjusted'
            sales_return.save(update_fields=['status'])

        elif refund_method == 'Refund to Customer':
            # Log a negative CustomerPayment to show money went out
            CustomerPayment.objects.create(
                customer=customer,
                payment_date=return_date,
                amount=-total_return,  # negative = outgoing refund
                payment_method='Cash',
                narration=f'Refund for {sales_return.return_number}',
                created_by=request.user if request.user.is_authenticated else None,
            )
            sales_return.status = 'Refunded'
            sales_return.save(update_fields=['status'])

        return redirect('invoice_return')


class InvoiceAddView(View):
    template_name = "pages/sales/invoice_add.html"

    def get(self, request):
        customers = Contact.objects.filter(contact_type__in=['Customer', 'Both'])
        products = Product.objects.all()
        today = timezone.now().date()
        
        # Serialize products for JavaScript to auto-populate Rate, Unit, Tax Type, Cost, Description
        product_list = list(products.values('id', 'name', 'code', 'selling_price', 'unit', 'purchase_price', 'description'))
        
        context = {
            'customers': customers,
            'products': products,
            'products_json': json.dumps(product_list, cls=DjangoJSONEncoder),
            'today': today,
        }
        return render(request, self.template_name, context)

    @transaction.atomic
    def post(self, request):
        customer_id = request.POST.get('customer')
        invoice_date = request.POST.get('invoice_date', timezone.now().date())
        due_date = request.POST.get('due_date') or None

        if not customer_id:
            return redirect('invoice_add')

        customer = get_object_or_404(Contact, id=customer_id)

        # 1. Create Invoice with new fields
        invoice = Invoice.objects.create(
            customer=customer,
            date=invoice_date,
            due_date=due_date,
            payment_terms=request.POST.get('payment_terms', 'Immediate'),
            sales_type=request.POST.get('sales_type', 'Goods'),
            sale_category=request.POST.get('sale_category', 'Local Sales'),
            vat_treatment=request.POST.get('vat_treatment', 'With VAT (13%)'),
            currency=request.POST.get('currency', 'NPR'),
            notes=request.POST.get('notes', ''),
            terms_conditions=request.POST.get('terms_conditions', ''),
            status='Draft',
            created_by=request.user if request.user.is_authenticated else None
        )

        # 2. Process Items
        product_ids = request.POST.getlist('product_id[]')
        quantities = request.POST.getlist('quantity[]')
        unit_prices = request.POST.getlist('unit_price[]')
        tax_types = request.POST.getlist('tax_type[]')
        units = request.POST.getlist('unit[]')

        subtotal_taxable = Decimal('0.00')
        subtotal_nontaxable = Decimal('0.00')
        total_vat = Decimal('0.00')
        total_discount = Decimal('0.00')  # Simplified for this pass
        total_cost = Decimal('0.00')
        total_gp = Decimal('0.00')

        for i in range(len(product_ids)):
            if not product_ids[i]: continue

            product = Product.objects.get(id=product_ids[i])
            qty = Decimal(quantities[i]) if quantities[i] else Decimal('0')
            price = Decimal(unit_prices[i]) if unit_prices[i] else Decimal('0.00')
            tax_type = tax_types[i] if i < len(tax_types) else 'Taxable'
            unit = units[i] if i < len(units) else 'Pcs'
            
            is_ret = True if qty < 0 else False
            
            # Simple line amount (excluding line-level discount for now to match UI screenshot)
            item_sub = price * qty
            
            vat_pct = Decimal('13.00') if tax_type == 'Taxable' else Decimal('0.00')
            vat_amt = item_sub * (vat_pct / Decimal('100.0'))
            item_tot = item_sub + vat_amt

            if tax_type == 'Taxable':
                subtotal_taxable += item_sub
            else:
                subtotal_nontaxable += item_sub
                
            total_vat += vat_amt

            # Internal
            item_cost_total = product.purchase_price * qty
            item_gp = item_sub - item_cost_total
            total_cost += item_cost_total
            total_gp += item_gp

            InvoiceItem.objects.create(
                invoice=invoice,
                product=product,
                item_code=product.code,
                unit=unit,
                quantity=qty,
                is_return=is_ret,
                unit_price=price,
                tax_type=tax_type,
                taxable_amount=item_sub if tax_type == 'Taxable' else Decimal('0'),
                vat_percentage=vat_pct,
                vat_amount=vat_amt,
                total_price=item_tot,
                cost_price=product.purchase_price,
                gross_profit=item_gp
            )

        grand_total = subtotal_taxable + subtotal_nontaxable + total_vat
        
        # Round off (if passed from JS)
        round_off = request.POST.get('round_off', '0.00')
        invoice.round_off = Decimal(round_off) if round_off else Decimal('0.00')
        grand_total += invoice.round_off

        # Update Invoice Totals
        invoice.subtotal_taxable = subtotal_taxable
        invoice.subtotal_non_taxable = subtotal_nontaxable
        invoice.subtotal = subtotal_taxable + subtotal_nontaxable
        invoice.taxable_amount = subtotal_taxable
        invoice.vat_amount = total_vat
        invoice.total_amount = grand_total
        invoice.total_cost = total_cost
        invoice.gross_profit = total_gp
        if subtotal_taxable != Decimal('0.00'):
            invoice.margin_percentage = (total_gp / subtotal_taxable) * Decimal('100.0')

        # 3. Process Allocations
        alloc_roles = request.POST.getlist('alloc_role[]')
        alloc_parties = request.POST.getlist('alloc_party[]')
        alloc_bases = request.POST.getlist('alloc_basis[]')
        alloc_values = request.POST.getlist('alloc_value[]')

        for i in range(len(alloc_roles)):
            if not alloc_roles[i]: continue

            basis = alloc_bases[i] if i < len(alloc_bases) else 'Fixed'
            val = Decimal(alloc_values[i]) if alloc_values[i] else Decimal('0.00')
            if basis == 'Percentage':
                alloc_amt = grand_total * (val / Decimal('100.0'))
            else:
                alloc_amt = val

            InvoiceAllocation.objects.create(
                invoice=invoice,
                role=alloc_roles[i],
                party_name=alloc_parties[i] if i < len(alloc_parties) else '',
                basis=basis,
                value=val,
                allocated_amount=alloc_amt
            )

        # 4. Process Payments
        paid_amount_str = request.POST.get('paid_amount', '0')
        if not paid_amount_str: paid_amount_str = '0'
        paid_amount = Decimal(paid_amount_str)
        payment_method = request.POST.get('payment_method', 'Cash')
        reference_no = request.POST.get('reference_no', '')
        narration = request.POST.get('narration', '')
        payment_date_str = request.POST.get('payment_date', '')
        payment_date = invoice_date
        if payment_date_str:
            try:
                from datetime import date
                payment_date = date.fromisoformat(payment_date_str)
            except ValueError:
                payment_date = invoice_date

        if paid_amount > 0:
            payment = CustomerPayment.objects.create(
                customer=customer,
                invoice=invoice,
                amount=paid_amount,
                payment_date=payment_date,
                payment_method=payment_method,
                status='Fully Allocated',
                created_by=request.user if request.user.is_authenticated else None
            )

            # Check if manual per-invoice allocations were submitted
            alloc_invoice_ids = request.POST.getlist('alloc_invoice_id[]')
            alloc_amounts = request.POST.getlist('alloc_amount[]')

            if alloc_invoice_ids:
                total_allocated = Decimal('0')
                # Manual allocation: apply to each specified old invoice
                for i, inv_id in enumerate(alloc_invoice_ids):
                    if not inv_id: continue
                    amt_str = alloc_amounts[i] if i < len(alloc_amounts) else '0'
                    try:
                        amt = Decimal(amt_str)
                    except Exception:
                        amt = Decimal('0')
                    if amt <= 0: continue
                    try:
                        old_inv = Invoice.objects.get(id=inv_id, customer=customer)
                        PaymentAllocation.objects.create(
                            payment=payment,
                            invoice=old_inv,
                            amount=amt
                        )
                        old_inv.paid_amount += amt
                        if old_inv.paid_amount >= old_inv.total_amount:
                            old_inv.status = 'Paid'
                        else:
                            old_inv.status = 'Partially Paid'
                        old_inv.save()
                        total_allocated += amt
                    except Invoice.DoesNotExist:
                        pass
                
                # Apply whatever is left to the current invoice
                remaining_for_current = paid_amount - total_allocated
                if remaining_for_current > 0:
                    PaymentAllocation.objects.create(
                        payment=payment,
                        invoice=invoice,
                        amount=remaining_for_current
                    )
                    invoice.paid_amount = remaining_for_current
            else:
                # Default: allocate entirely to current invoice
                PaymentAllocation.objects.create(
                    payment=payment,
                    invoice=invoice,
                    amount=paid_amount
                )
                invoice.paid_amount = paid_amount

        # Determine Status
        if invoice.paid_amount >= invoice.total_amount:
            invoice.status = 'Paid'
        elif invoice.paid_amount > 0:
            invoice.status = 'Partially Paid'
        else:
            invoice.status = 'Unpaid'

        invoice.save()

        return redirect('invoice')

class QuotationView(TemplateView):
    template_name = "pages/sales/quotation.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["quotations"] = Quotation.objects.select_related('customer').order_by('-date', '-id')
        return context

class QuotationAddView(View):
    template_name = "pages/sales/quotation_add.html"

    def get(self, request):
        customers = Contact.objects.filter(contact_type__in=['Customer', 'Both'])
        products = Product.objects.all()
        today = timezone.now().date()
        
        product_list = list(products.values('id', 'name', 'code', 'selling_price', 'unit', 'purchase_price', 'description'))
        
        context = {
            'customers': customers,
            'products': products,
            'products_json': json.dumps(product_list, cls=DjangoJSONEncoder),
            'today': today,
        }
        return render(request, self.template_name, context)

    @transaction.atomic
    def post(self, request):
        customer_id = request.POST.get('customer')
        quote_date = request.POST.get('date', timezone.now().date())
        valid_until = request.POST.get('valid_until') or None

        if not customer_id:
            return redirect('quotation_add')

        customer = get_object_or_404(Contact, id=customer_id)

        quotation = Quotation.objects.create(
            customer=customer,
            date=quote_date,
            valid_until=valid_until,
            status=request.POST.get('status', 'Draft'),
            currency=request.POST.get('currency', 'NPR'),
            notes=request.POST.get('notes', ''),
            created_by=request.user if request.user.is_authenticated else None
        )

        product_ids = request.POST.getlist('product_id[]')
        quantities = request.POST.getlist('quantity[]')
        unit_prices = request.POST.getlist('unit_price[]')
        tax_types = request.POST.getlist('tax_type[]')
        units = request.POST.getlist('unit[]')

        subtotal = Decimal('0.00')
        total_vat = Decimal('0.00')

        for i in range(len(product_ids)):
            if not product_ids[i]: continue

            product = Product.objects.get(id=product_ids[i])
            qty = Decimal(quantities[i]) if quantities[i] else Decimal('0')
            price = Decimal(unit_prices[i]) if unit_prices[i] else Decimal('0.00')
            tax_type = tax_types[i] if i < len(tax_types) else 'Taxable'
            unit = units[i] if i < len(units) else 'Pcs'
            
            line_amt = price * qty
            vat_pct = Decimal('13.00') if tax_type == 'Taxable' else Decimal('0.00')
            vat_amt = line_amt * (vat_pct / Decimal('100.0'))
            item_tot = line_amt + vat_amt

            subtotal += line_amt
            total_vat += vat_amt

            QuotationItem.objects.create(
                quotation=quotation,
                product=product,
                unit=unit,
                quantity=qty,
                rate=price,
                tax_type=tax_type,
                tax_amount=vat_amt,
                amount=item_tot
            )

        grand_total = subtotal + total_vat
        
        round_off = request.POST.get('round_off', '0.00')
        quotation.round_off = Decimal(round_off) if round_off else Decimal('0.00')
        grand_total += quotation.round_off

        quotation.subtotal = subtotal
        quotation.vat_amount = total_vat
        quotation.total_amount = grand_total
        quotation.save()

        return redirect('quotation')

class CustomersView(TemplateView):
    template_name = "pages/sales/customers.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customers = Contact.objects.filter(contact_type__in=['Customer', 'Both']).annotate(
            num_bills=Count('invoice')
        ).order_by('-created_at')
        
        # Calculate stats
        total_customers = customers.count()
        total_bills = Invoice.objects.count()
        total_receivables = Invoice.objects.exclude(status='Paid').aggregate(
            due=Sum('total_amount') - Sum('paid_amount')
        )['due'] or Decimal('0.00')
        
        # Active this month (has invoices created this month)
        current_month = timezone.now().month
        active_this_month = Invoice.objects.filter(date__month=current_month).values('customer').distinct().count()

        context["title"] = "Customers Dashboard"
        context["customers"] = customers
        context["total_customers"] = total_customers
        context["total_bills"] = total_bills
        context["total_receivables"] = total_receivables
        context["active_this_month"] = active_this_month
        return context

class CustomerDetailAPIView(View):
    def get(self, request, pk):
        customer = get_object_or_404(Contact, id=pk)

        from django.db.models import Sum
        # Stats
        total_bills   = Invoice.objects.filter(customer=customer).count()
        total_sales   = float(Invoice.objects.filter(customer=customer).aggregate(s=Sum('total_amount'))['s'] or 0)
        total_received = float(Invoice.objects.filter(customer=customer).aggregate(s=Sum('paid_amount'))['s'] or 0)
        total_returns  = float(customer.sales_returns.aggregate(s=Sum('total_amount'))['s'] or 0)
        outstanding    = float(customer.outstanding_balance())

        # Transactions — all types, merged & sorted
        transactions = []
        for inv in Invoice.objects.filter(customer=customer).order_by('-date')[:20]:
            transactions.append({
                'date': inv.date.strftime("%Y-%m-%d"),
                'type': 'Sales Invoice',
                'ref': inv.invoice_number,
                'total_amount': float(inv.total_amount),
                'paid_amount': float(inv.paid_amount),
                'due_amount': float(inv.total_amount - inv.paid_amount),
                'due_days': 0,
                'css_class': 'type-sale',
                'detail_url': f'/sales/invoice/{inv.id}/'
            })
        for pay in CustomerPayment.objects.filter(customer=customer).order_by('-payment_date')[:20]:
            is_refund = pay.amount < 0
            transactions.append({
                'date': pay.payment_date.strftime("%Y-%m-%d"),
                'type': 'Refund Issued' if is_refund else 'Payment Received',
                'ref': pay.payment_number,
                'total_amount': float(pay.amount),
                'paid_amount': float(pay.amount),
                'due_amount': 0,
                'due_days': 0,
                'css_class': 'type-refund' if is_refund else 'type-payment',
                'detail_url': f'/sales/customer-payment/{pay.id}/'
            })
        for ret in customer.sales_returns.order_by('-return_date')[:20]:
            transactions.append({
                'date': ret.return_date.strftime("%Y-%m-%d"),
                'type': 'Sales Return',
                'ref': ret.return_number,
                'total_amount': float(ret.total_amount),
                'paid_amount': 0,
                'due_amount': 0,
                'due_days': 0,
                'css_class': 'type-return',
                'detail_url': f'/sales/invoice/return/{ret.id}/'
            })
        transactions.sort(key=lambda x: x['date'], reverse=True)
        
        contact_persons = []
        for person in customer.persons.all():
            contact_persons.append({
                'name': person.name,
                'designation': person.designation or 'Contact',
                'phone': person.phone or '',
                'email': person.email or ''
            })
        
        data = {
            'id': customer.id,
            'name': customer.name,
            'initials': customer.name[:2].upper() if customer.name else "N/A",
            'email': customer.email or "N/A",
            'phone': customer.phone or "N/A",
            'address': customer.address or "N/A",
            'pan_vat': customer.pan_vat_number or "N/A",
            'vat_registered': customer.vat_registered,
            'contact_person': customer.contact_person or "N/A",
            'contact_persons': contact_persons,
            'outstanding': outstanding,
            'credit_limit': float(customer.credit_limit),
            'total_bills': total_bills,
            'total_sales': total_sales,
            'total_received': total_received,
            'total_returns': total_returns,
            'transactions': transactions
        }
        return JsonResponse(data)

class CustomerAddAPIView(View):
    def post(self, request):
        customer_id = request.POST.get('customer_id')
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        pan_vat = request.POST.get('pan_vat')
        address = request.POST.get('address')

        if not name:
            return JsonResponse({'status': 'error', 'message': 'Name is required'}, status=400)

        if customer_id:
            customer = get_object_or_404(Contact, id=customer_id)
            customer.name = name
            customer.phone = phone
            customer.pan_vat_number = pan_vat
            customer.address = address
            customer.save()
            # Delete old contact persons to replace them
            customer.persons.all().delete()
        else:
            customer = Contact.objects.create(
                name=name,
                phone=phone,
                pan_vat_number=pan_vat,
                address=address,
                opening_balance=Decimal('0.00'),
                credit_limit=Decimal('0.00'),
                contact_type='Customer'
            )

        # Save multiple contact persons
        cp_names        = request.POST.getlist('cp_name[]')
        cp_designations = request.POST.getlist('cp_designation[]')
        cp_phones       = request.POST.getlist('cp_phone[]')
        cp_emails       = request.POST.getlist('cp_email[]')

        for i, cp_name in enumerate(cp_names):
            if not cp_name.strip():
                continue  # skip empty rows
            ContactPerson.objects.create(
                contact=customer,
                name=cp_name.strip(),
                designation=cp_designations[i] if i < len(cp_designations) else '',
                phone=cp_phones[i] if i < len(cp_phones) else '',
                email=cp_emails[i] if i < len(cp_emails) else '',
            )

        # Set contact_person to first contact's name for legacy display
        first_cp = customer.persons.first()
        if first_cp:
            Contact.objects.filter(pk=customer.pk).update(contact_person=first_cp.name)

        return JsonResponse({'status': 'success', 'id': customer.id, 'name': customer.name})



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
            amount = Decimal(amount_str)
            invoice = Invoice.objects.get(id=invoice_id, customer_id=customer_id)
        except (ValueError, Invoice.DoesNotExist, Exception):
            return redirect('customer_payment_add')

        # Enforce that payment cannot exceed total amount
        pending_amount = invoice.total_amount - invoice.paid_amount
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
        ).order_by('date')
        data = []
        for inv in invoices:
            pending = inv.total_amount - inv.paid_amount
            if pending > 0:
                data.append({
                    'id': inv.id,
                    'invoice_no': str(inv.id).zfill(6),  # Use INV-XXXXXX format
                    'date': inv.date.strftime('%d/%m/%Y'),
                    'total_amount': str(inv.total_amount),
                    'paid_amount': str(inv.paid_amount),
                    'pending_amount': str(pending),
                })
        return JsonResponse({'invoices': data})


# ==================== INVENTORY ====================

class InventoryView(TemplateView):
    template_name = "pages/inventory/inventory.html"


class InventoryProductView(View):
    template_name = "pages/inventory/inventory_product.html"

    def get(self, request):
        products = Product.objects.select_related('category').order_by('name')
        categories = ProductCategory.objects.all()
        context = {
            "title": "Products",
            "products": products,
            "categories": categories,
            "total": products.count(),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        """Handle quick-add product from modal form."""
        name = request.POST.get('name')
        if not name:
            return redirect('inventory_product')

        code = request.POST.get('code') or None
        product_type = request.POST.get('product_type', 'Goods')
        category_id = request.POST.get('category') or None
        unit = request.POST.get('unit', 'Pcs')
        purchase_price = request.POST.get('purchase_price', '0.00') or '0.00'
        selling_price = request.POST.get('selling_price', '0.00') or '0.00'
        description = request.POST.get('description', '')

        Product.objects.create(
            name=name,
            code=code,
            product_type=product_type,
            category_id=category_id if category_id else None,
            unit=unit,
            purchase_price=Decimal(purchase_price),
            selling_price=Decimal(selling_price),
            description=description,
        )
        return redirect('inventory_product')


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
        context["tabs"] = ["Approved", "Draft"]
        context["expenses"] = Expense.objects.select_related('category').order_by('-date')
        context["new_url"] = "expenses_add"
        return context

class ExpensesAddView(View):
    template_name = "pages/purchase/expenses_add.html"

    def get(self, request):
        suppliers = Contact.objects.filter(contact_type__in=['Supplier', 'Both'])
        context = {
            "title": "Add New Expense",
            "suppliers": suppliers,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        # 1. Parse date and description
        expense_date = request.POST.get('invoice_date')
        description = request.POST.get('expense_notes', '')

        # 2. Get the accounts and amounts
        account_names = request.POST.getlist('account_name[]')
        account_amounts = request.POST.getlist('account_amount[]')

        # 3. Calculate total amount and determine category
        total_amount = Decimal('0.00')
        category_name = "General Expense"
        
        if account_names:
            category_name = account_names[0]  # Use the first account as the category
            
        for amt in account_amounts:
            try:
                total_amount += Decimal(amt)
            except:
                pass

        # 4. Find or create the ExpenseCategory
        category, _ = ExpenseCategory.objects.get_or_create(name=category_name)

        # 5. Create the Expense
        Expense.objects.create(
            category=category,
            amount=total_amount,
            date=expense_date,
            payment_method='Cash',
            description=description
        )

        return redirect('expenses')



class SupplierPaymentView(TemplateView):
    template_name = "pages/purchase/supplier_payment.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Supplier Payments"
        context["tabs"] = ["Approved", "Draft"]
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
            amount = Decimal(amount_str)
            bill = PurchaseBill.objects.get(id=bill_id, supplier_id=supplier_id)
        except (ValueError, PurchaseBill.DoesNotExist, Exception):
            return redirect('supplier_payment_add')

        # Enforce that payment cannot exceed total amount
        pending_amount = bill.total_amount - bill.paid_amount
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