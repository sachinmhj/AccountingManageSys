from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "pages/home.html"


class SalesView(TemplateView):
    template_name = "pages/sales.html"


# ==================== SALES ====================

class InvoiceView(TemplateView):
    template_name = "pages/sales/invoice.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Invoice"
        context["tabs"] = ["Approved", "Draft"]
        context["new_url"] = "invoice_add"
        
        # Approved and Draft list data
        context["approved_invoices"] = []
        context["draft_invoices"] = []
        return context


class InvoiceAddView(TemplateView):
    template_name = "pages/sales/invoice_add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add New Invoice"
        return context

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
        context["tabs"] = ["Approved", "Draft"]
        context["payments"] = []
        context["new_url"] = "customer_payment_add"
        return context


class CustomerPaymentAddView(TemplateView):
    template_name = "pages/sales/customer_payment_add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "New Customer Payment"
        return context


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
        context["new_action"] = "openProductModal()"
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
        context["new_action"]="openCategoryModal()"
        return context

class UnitsMeasurementView(TemplateView):
    template_name = "pages/inventory/units_measurement.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Units Of Measurement"
        context["categories"] = []
        context["new_action"]="openCreateUnitModal()"
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
        context["title"] = "Purchase"
        context["tabs"] = ["Approved", "Draft"]
        context["purchases"] = []
        context["new_url"] = "purchase_add"
        return context

class PurchaseAddView(TemplateView):
    template_name = "pages/purchase/purchase_add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add New Purchase Bill"
        return context
    


class ExpensesView(TemplateView):
    template_name = "pages/purchase/expenses.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Expenses"
        context["tabs"] = ["Approved", "Draft"]
        context["expenses"] = []
        context["new_url"] = "expenses_add"
        return context

class ExpensesAddView(TemplateView):
    template_name ="pages/purchase/expenses_add.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Add New Expenses"
        return context



class SupplierPaymentView(TemplateView):
    template_name = "pages/purchase/supplier_payment.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Suppliers Payment"
        context["tabs"] = ["Approved", "Draft"]
        context["payments"] = []
        context["new_url"] = "supplier_add"
        return context
    
class SupplierAddView(TemplateView):
    template_name ="pages/purchase/supplier_add.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "New Supplier Payment"
        return context