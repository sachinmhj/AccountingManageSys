from django.views.generic import TemplateView



class HomeView(TemplateView):
    template_name = "pages/home.html"



class SalesView(TemplateView):
    template_name = "pages/sales.html"




class InvoiceView(TemplateView):

    template_name = "pages/sales/invoice.html"


    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)


        context["title"] = "Invoice"

        context["tabs"] = [
            "Approved",
            "Draft"
        ]

        context["invoices"] = []


        return context





class CustomerPaymentView(TemplateView):

    template_name = "pages/sales/customer_payment.html"


    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)


        context["title"] = "Customer Payments"


        context["tabs"] = [
            "Approved",
            "Draft"
        ]


        context["payments"] = []


        return context






class InventoryView(TemplateView):

    template_name = "pages/inventory/inventory.html"

class InventoryProductView(TemplateView):
    template_name = "pages/inventory/inventory_product.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Products"
        context["tabs"] = [
            "Goods",
            "Services"
        ]
        context["products"] = []
        return context
    

class VariantProductView(TemplateView):
    template_name = "pages/inventory/variant_product.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Variant Products"
        context["tabs"] = [
            "Product",
            "Service"
        ]
        context["products"] = []
        return context

class VariantAttributeView(TemplateView):
    template_name = "pages/inventory/variant_attribute.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Variant Attributes"
        context["attributes"] = []
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

        context["tabs"] = [
            "Approved",
            "Draft"
        ]

        context["transfers"] = []

        return context

class InventoryAdjustmentView(TemplateView):

    template_name = "pages/inventory/inventory_adjust.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["title"] = "Inventory Adjustment"

        context["tabs"] = [
            "Approved",
            "Draft"
        ]

        context["adjusts"] = []

        return context

class BillMaterialView(TemplateView):

    template_name = "pages/inventory/bills_material.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["title"] = "Bill of Materials"

        context["bills"] = []

        return context

class ProductionOrderView(TemplateView):

    template_name = "pages/inventory/production_order.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["title"] = "Production Order"

        context["tabs"] = [
            "Approved",
            "Draft"
        ]

        context["orders"] = []

        return context

class ProductionJournalView(TemplateView):

    template_name = "pages/inventory/production_journal.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["title"] = "Production Journal"

        context["tabs"] = [
            "Approved",
            "Draft"
        ]

        context["journals"] = []

        return context






class PurchaseView(TemplateView):

    template_name = "pages/purchase/purchase.html"

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["title"] = "Purchase"

        context["tabs"] = [
            "Approved",
            "Draft"
        ]

        context["purchases"] = []

        return context

class ExpensesView(TemplateView):

    template_name = "pages/purchase/expenses.html"


    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["title"] = "Expenses"

        context["tabs"] = [
            "Approved",
            "Draft"
        ]

        context["expenses"] = []

        return context

class SupplierPaymentView(TemplateView):

    template_name = "pages/purchase/supplier_payment.html"


    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["title"] = "Suppliers Payment"

        context["tabs"] = [
            "Approved",
            "Draft"
        ]

        context["payments"] = []

        return context