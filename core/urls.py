from django.urls import path
from .views import (
    HomeView,
    SalesView,
    InvoiceView,
    CustomerPaymentView,
    InventoryView,
    PurchaseView,
    ExpensesView,
    SupplierPaymentView,
    InventoryProductView,
)
urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("sales/", SalesView.as_view(), name="sales"),
    path("sales/invoice/",InvoiceView.as_view(),name="invoice"),
    path("sales/customer-payment/",CustomerPaymentView.as_view(),name="customer_payment"),  
    path("inventory/",InventoryView.as_view(),name="inventory"),
    path("inventory/product/",InventoryProductView.as_view(),name="inventory_product"),
    path("purchase/",PurchaseView.as_view(),name="purchase"),
    path("purchase/expenses/", ExpensesView.as_view(), name="expenses"),
    path("purchase/supplier-payment/",SupplierPaymentView.as_view(),name="supplier_payment"),

]