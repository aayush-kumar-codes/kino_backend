from django.urls import path
from .views import (
    CreatePlanAPI, CreateBenefitAPI, GetPlan, FinanceAPI,
    GraphDataAPI, InvoiceAPI, InvoiceListAPI, InvoicePreData
)

urlpatterns = [
    # URL pattern for school create/get/update/delete
    path('plan/', CreatePlanAPI.as_view(), name='create_plan'),
    path('benefit/', CreateBenefitAPI.as_view(), name='create_benefit'),
    path('plans/', GetPlan.as_view(), name='get_plan'),
    path('finance/', FinanceAPI.as_view(), name='finance'),
    path('graph/', GraphDataAPI.as_view(), name='graph'),
    path('invoice/', InvoiceAPI.as_view(), name='Create_Invoice'),
    path('invoice/<int:pk>/', InvoiceAPI.as_view(), name='view'),
    path('invoices_data/', InvoiceListAPI.as_view(), name='list_all_invoice'),
    path('invoice_pre/', InvoicePreData.as_view(), name='invoice_pre'),

]
