from django.urls import path
from .views import (
    SchoolAPI, GetSchoolListAPI,
    TermAPI, AllTermsAPI, ClassAPI, LessonAPI,
    GetLessonListAPI, GetOrganizationsListAPI, SchoolDashboardAPI,
    LessonCoverageAPI, ClassesAPI, StudentDataAPI, TeacherDataAPI,
    ParentDataAPI, SchoolDetailsAPI
)

urlpatterns = [
    # URL pattern for school create/get/update/delete
    path('create_school/', SchoolAPI.as_view(), name='create_school'),
    path('create_school/<int:pk>/', SchoolAPI.as_view(), name='school_by_pk'),
    path('school/', GetSchoolListAPI.as_view({'get': 'list'}), name='get_schools'),
    path('school/<int:pk>/', GetSchoolListAPI.as_view({'get': 'list'}), name='get_schools_by_pk'),

    # URL pattern for term create/get/update/delete
    path('term/', TermAPI.as_view(), name='create_term'),
    path('term/<int:pk>/', TermAPI.as_view(), name='term_by_id'),
    path('get_term/', AllTermsAPI.as_view(), name='get_term'),

    path('class/', ClassAPI.as_view(), name='class'),
    path('class/<int:pk>/', ClassAPI.as_view(), name='class'),

    # URL pattern for lesson create/get/update/delete
    path('lesson/', LessonAPI.as_view(), name='create_lesson'),
    path('lesson/<int:pk>/', LessonAPI.as_view(), name='lesson_by_id'),
    path('get_lessons/', GetLessonListAPI.as_view({'get': 'list'}), name='get_lessons'),
    path('get_lessons/<int:pk>/', GetLessonListAPI.as_view({'get': 'list'}), name='get_lessons'),
    path('organization/', GetOrganizationsListAPI.as_view({'get': 'list'}), name='organization'),
    path('school/dashboard/', SchoolDashboardAPI.as_view(), name='dashboard'),
    path('coverage/', LessonCoverageAPI.as_view(), name='coverage'),
    path('classes_data/', ClassesAPI.as_view(), name='classes_data'),
    path('std_list/', StudentDataAPI.as_view({'get': 'list'}), name='std_list'),
    path('parent_list/', ParentDataAPI.as_view({'get': 'list'}), name='parent_list'),
    path('teacher_list/', TeacherDataAPI.as_view({'get': 'list'}), name='teacher_list'),
    path('school_detail/', SchoolDetailsAPI.as_view(), name='school_detail'),

]
