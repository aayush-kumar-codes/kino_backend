from django.urls import path
from .views import (
    RegisterAPI, LoginAPI, RequestAccessAPI, PasswordChangeAPI,
    LogoutAPI, UserRolesAPI, PermissionView, ActivityAPI, UpdateConfig,
    UpdatePasswordAPIView, DashboardAPI, ActivityAction, VerifyOTP
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

]
