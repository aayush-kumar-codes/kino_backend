from django.urls import path
from .views import (
    SchoolAPI, SchoolHeadAccess, GetSchoolListAPI,
    TermAPI, TermHeadAccess, AllTermsAPI, ClassAPI, LessonAPI,
    GetLessonListAPI
)

urlpatterns = [
    # URL pattern for school create/get/update/delete
    path('create_school/', SchoolAPI.as_view(), name='create_school'),
    path('school/', GetSchoolListAPI.as_view({'get': 'list'}), name='get_schools'),
    path('school/<int:pk>/', GetSchoolListAPI.as_view({'get': 'list'}), name='get_schools_by_pk'),

    # URL pattern for school by Head of Curicullum
    path('head_school/<int:pk>/', SchoolHeadAccess.as_view(), name='head_access'),

    # URL pattern for term create/get/update/delete
    path('term/', TermAPI.as_view(), name='create_term'),
    path('term/<int:pk>/', TermAPI.as_view(), name='term_by_id'),
    path('get_term/', AllTermsAPI.as_view(), name='get_term'),

    # URL pattern for term by Head of Curicullum
    path('head_term/<int:pk>/', TermHeadAccess.as_view(), name='head_term'),

    # URL pattern for term by Head of Curicullum
    path('class/', ClassAPI.as_view(), name='class'),
    path('class/<int:pk>/', ClassAPI.as_view(), name='class'),

    # URL pattern for lesson create/get/update/delete
    path('lesson/', LessonAPI.as_view(), name='create_lesson'),
    path('lesson/<int:pk>/', LessonAPI.as_view(), name='lesson_by_id'),
    path('get_lessons/', GetLessonListAPI.as_view({'get': 'list'}), name='get_lessons'),
    path('get_lessons/<int:pk>/', GetLessonListAPI.as_view({'get': 'list'}), name='get_lessons'),

    # # URL pattern for lession by Head of Curicullum
    # path('head_lession/<int:pk>/', LessionHeadAccess.as_view(), name='head_lession'),
]
