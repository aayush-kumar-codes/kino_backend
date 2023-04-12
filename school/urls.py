from django.urls import path
from .views import (
    CreateSchoolAPI, SchoolHeadAccess, GetSchoolListAPI
)

urlpatterns = [
    # URL pattern for school create/get/update/delete
    path('create_school/', CreateSchoolAPI.as_view(), name='create_school'),
    path('school/', GetSchoolListAPI.as_view({'get': 'list'}), name='get_schools'),
    path('school/<int:pk>/', GetSchoolListAPI.as_view({'get': 'list'}), name='get_schools by pk'),

    # URL pattern for school by Head of Curicullum
    path('head_school/<int:pk>/', SchoolHeadAccess.as_view(), name='head_access'),

]
