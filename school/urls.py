from django.urls import path
from .views import (
    CreateSchoolAPI, SchoolHeadAccess, GetSchoolListAPI,
    CreateTermAPI, TermHeadAccess, GetAllTermsAPI
)

urlpatterns = [
    # URL pattern for school create/get/update/delete
    path('create_school/', CreateSchoolAPI.as_view(), name='create_school'),
    path('school/', GetSchoolListAPI.as_view({'get': 'list'}), name='get_schools'),
    path('school/<int:pk>/', GetSchoolListAPI.as_view({'get': 'list'}), name='get_schools_by_pk'),

    # URL pattern for school by Head of Curicullum
    path('head_school/<int:pk>/', SchoolHeadAccess.as_view(), name='head_access'),

    # URL pattern for term create/get/update/delete
    path('term/', CreateTermAPI.as_view(), name='create_term'),
    path('term/<int:pk>/', CreateTermAPI.as_view(), name='term_by_id'),
    path('get_term/', GetAllTermsAPI.as_view(), name='get_term'),

    # URL pattern for term by Head of Curicullum
    path('head_term/<int:pk>/', TermHeadAccess.as_view(), name='head_term'),

    # # URL pattern for lession create/get/update/delete
    # path('create_lession/', CreateLessionAPI.as_view(), name='create_lession'),
    # path('lession_by_id/<int:pk>/', CreateLessionAPI.as_view(), name='lession_by_id'),
    # path('get_lessions/', GetLesssionAPI.as_view(), name='get_lessions'),
    # path('search_lession/', LessionViewSet.as_view({'get': 'list'}), name='search_lession'),

    # # URL pattern for lession by Head of Curicullum
    # path('head_lession/<int:pk>/', LessionHeadAccess.as_view(), name='head_lession'),
]
