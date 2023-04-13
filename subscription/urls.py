from django.urls import path
from .views import (
    CreatePlanAPI, CreateBenefitAPI
)

urlpatterns = [
    # URL pattern for school create/get/update/delete
    path('plan/', CreatePlanAPI.as_view(), name='create_plan'),
    path('benefit/', CreateBenefitAPI.as_view(), name='create_benefit'),

]
