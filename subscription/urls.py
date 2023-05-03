from django.urls import path
from .views import (
    CreatePlanAPI, CreateBenefitAPI, GetPlan, FinanceAPI,
    GraphDataAPI
)

urlpatterns = [
    # URL pattern for school create/get/update/delete
    path('plan/', CreatePlanAPI.as_view(), name='create_plan'),
    path('benefit/', CreateBenefitAPI.as_view(), name='create_benefit'),
    path('plans/', GetPlan.as_view(), name='get_plan'),
    path('finance/', FinanceAPI.as_view(), name='finance'),
    path('graph/', GraphDataAPI.as_view(), name='graph'),

]
