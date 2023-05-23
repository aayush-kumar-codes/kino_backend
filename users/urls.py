from django.urls import path
from .views import (
    RegisterAPI, LoginAPI, RequestAccessAPI, PasswordChangeAPI,
    LogoutAPI, UserRolesAPI, PermissionView, ActivityAPI, UpdateConfig,
    UpdatePasswordAPIView, DashboardAPI, ActivityAction, VerifyOTP,
    GetParentListAPI, GetTeacherListAPI, GetStudentListAPI,
    ClassBasedStudentCount, ClassBasedParentCount, StudentAPI, TeacherAPI,
    ParentAPI, GetAllParentsAPI, RollCallAPI, RollCallBarGraphAPI,
    RollCallPieChartAPI
)
from rest_framework_simplejwt.views import (
    TokenRefreshView
)

# Define URL patterns for the API
urlpatterns = [
    # URL pattern for user registration/signup
    path('signup/', RegisterAPI.as_view(), name='signup'),

    # URL pattern for user login/authentication
    path('login/', LoginAPI.as_view(), name='login'),

    # URL pattern for user logout
    path('logout/', LogoutAPI.as_view(), name='logout'),

    # URL pattern for refreshing JWT tokens
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # URL pattern for requesting access to some resource
    path('request_access/', RequestAccessAPI.as_view(), name='request_access'),

    # URL pattern for changing user password
    path('change_password/', PasswordChangeAPI.as_view(), name='change_password'),

    path('role/', UserRolesAPI.as_view(), name='roles_by_admin'),
    path('role/<int:pk>/', UserRolesAPI.as_view(), name='roles_by_admin'),

    path('permissions/', PermissionView.as_view(), name='permission_list'),

    path('activity/', ActivityAPI.as_view(), name='activity'),
    path('config/', UpdateConfig.as_view(), name='config'),
    path('password/', UpdatePasswordAPIView.as_view(), name='password'),
    path('dashboard/', DashboardAPI.as_view(), name='dashboard'),
    path('active_status/', ActivityAction.as_view(), name='active_status'),
    path('verify_otp/', VerifyOTP.as_view(), name='verify_otp'),

    path('parent/', ParentAPI.as_view(), name='parent'),
    path('parent_search/', GetParentListAPI.as_view({'get': 'list'}), name='parent_search'),
    path('parent_search/<int:pk>/', GetParentListAPI.as_view({'get': 'list'}), name='parent_search_by_id'),

    path('class_parent_count/', ClassBasedParentCount.as_view(), name='class_parent_count'),

    path('teacher/', TeacherAPI.as_view(), name='taecher'),
    path('teacher_search/', GetTeacherListAPI.as_view({'get': 'list'}), name='teacher_search'),
    path('teacher_search/<int:pk>/', GetTeacherListAPI.as_view({'get': 'list'}), name='teacher_search_by_id'),

    path('student/', StudentAPI.as_view(), name='student'),
    path('student_search/', GetStudentListAPI.as_view({'get': 'list'}), name='student_search'),
    path('student_search/<int:pk>/', GetStudentListAPI.as_view({'get': 'list'}), name='student_search_by_id'),

    path('class_std_count/', ClassBasedStudentCount.as_view(), name='class_std_count'),
    path('all_parents/', GetAllParentsAPI.as_view(), name='all_parents'),

    path('roll_call/', RollCallAPI.as_view(), name='roll_call'),
    path('roll_call_graph/', RollCallBarGraphAPI.as_view(), name='roll_call_graph'),
    path('roll_call_pie/', RollCallPieChartAPI.as_view(), name='roll_call_pie'),

]
