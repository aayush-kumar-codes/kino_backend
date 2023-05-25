from django.urls import path
from .views import (
    CreatePlanAPI, CreateBenefitAPI, GetPlan, FinanceAPI,
    GraphDataAPI, InvoiceAPI, InvoiceListAPI, InvoicePreData,
    SchoolSubscriptionAPI, AccountPersonalAPI, SchoolPaymentHistoryAPI,
    SchoolInvoiceAPI, SchoolCancelPlanAPI
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

    path('school_subscription/', SchoolSubscriptionAPI.as_view(), name='school_subscription'),
    path('user_data/', AccountPersonalAPI.as_view(), name='user_data'),
    path('payment_history/', SchoolPaymentHistoryAPI.as_view(), name='payment_history'),
    path('school_invoice/', SchoolInvoiceAPI.as_view(), name='school_invoice'),
    path('school_plan_cancel/', SchoolCancelPlanAPI.as_view(), name='school_plan_cancel'),

]
