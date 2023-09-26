from rest_framework.permissions import BasePermission
from users.models import User
from enum import Enum
from utils.helper import get_view_permissions
from auth0.authentication.token_verifier import TokenVerifier, AsymmetricSignatureVerifier

from auth0.authentication.token_verifier import TokenValidationError
from django.conf import settings
from rest_framework.authentication import BaseAuthentication

domain = settings.AUTH_0_DOMAIN
client_id = settings.AUTH_0_CLIENT_ID


from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

class CustomAuthentication(BaseAuthentication):
    def authenticate(self, request):
        # Implement your custom authentication logic here
        # Return a tuple of (user, auth) if authentication is successful
        # Return None if authentication fails
        
        # For example, you can authenticate based on a custom header:
        # auth_header = request.META.get('HTTP_X_CUSTOM_AUTH_HEADER')
        
        # if not auth_header:
        #     return None  # Authentication failed
        
        # Perform your custom authentication logic here, such as validating tokens, API keys, etc.
        # If authentication is successful, return a user object and None for auth
        # If authentication fails, raise AuthenticationFailed
        
        # Example of token validation (replace with your actual logic):
        try:
            print("JTDFGHJNBVBFGHNBVBFGYJUGFYTR^&V^%^T*&()")
            id_token = request.META.HTTP_AUTHORIZATION.split(" ")[-1]
            print("YFGBNUHKM<", request.META.HTTP_AUTHORIZATION)
            jwks_url = 'https://{}/.well-known/jwks.json'.format(settings.AUTH_0_DOMAIN)
            issuer = 'https://{}/'.format(settings.AUTH_0_DOMAIN)

            sv = AsymmetricSignatureVerifier(jwks_url)  # Reusable instance
            tv = TokenVerifier(signature_verifier=sv, issuer=issuer, audience=settings.AUTH_0_AUDIENCE)

            tv.verify(str(id_token))
            return True
        except Exception:
            return False
        
        # Authentication failed
        raise AuthenticationFailed('Authentication failed')

    def authenticate_header(self, request):
        # Optionally, you can set a custom WWW-Authenticate header here.
        # This is used in the response when authentication fails.
        return 'Custom realm="api"'

class Auth0Permission(BasePermission):
    def has_permission(self, request, view):
        print("HTRTBYUIOBUGYHNIJOHYUGUHN")
        try:
            print("JTDFGHJNBVBFGHNBVBFGYJUGFYTR^&V^%^T*&()")
            id_token = request.META.HTTP_AUTHORIZATION.split(" ")[-1]
            print("YFGBNUHKM<", request.META.HTTP_AUTHORIZATION)
            jwks_url = 'https://{}/.well-known/jwks.json'.format(settings.AUTH_0_DOMAIN)
            issuer = 'https://{}/'.format(settings.AUTH_0_DOMAIN)

            sv = AsymmetricSignatureVerifier(jwks_url)  # Reusable instance
            tv = TokenVerifier(signature_verifier=sv, issuer=issuer, audience=settings.AUTH_0_AUDIENCE)

            tv.verify(str(id_token))
            return True
        except Exception:
            return False

class AdminAccess(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.role == User.Admin:
            return True
        return False


class TeacherAccess(BasePermission):
    def has_permission(self, request, view):
        if request.user.role == User.Admin:
            return True
        required_permissions, permissions = get_view_permissions(request, view)
        if request.user and request.user.role == User.Teacher:
            if required_permissions in list(permissions):
                return True
        return False


class StudentAccess(BasePermission):
    def has_permission(self, request, view):
        if request.user.role == User.Admin:
            return True
        required_permissions, permissions = get_view_permissions(request, view)
        if request.user and request.user.role == User.Student:
            if required_permissions in list(permissions):
                return True
        return False


class ParentAccess(BasePermission):
    def has_permission(self, request, view):
        if request.user.role == User.Admin:
            return True
        required_permissions, permissions = get_view_permissions(request, view)

        if request.user and request.user.role == User.Parent:
            if required_permissions in list(permissions):
                return True
        return False


class HeadOfCuricullumAccess(BasePermission):
    def has_permission(self, request, view):
        if request.user.role == User.Admin:
            return True

        required_permissions, permissions = get_view_permissions(request, view)
        if request.user and request.user.role == User.Head_of_curicullum:
            if required_permissions in list(permissions):
                return True
        return False


class ContentCreatorAccess(BasePermission):
    def has_permission(self, request, view):
        if request.user.role == User.Admin:
            return True
        required_permissions, permissions = get_view_permissions(request, view)

        if request.user and request.user.role in [User.Content_creator, User.Head_of_curicullum]:
            if required_permissions in list(permissions):
                return True
        return False


class FinanceAccess(BasePermission):
    def has_permission(self, request, view):
        if request.user.role == User.Admin:
            return True
        required_permissions, permissions = get_view_permissions(request, view)
        if request.user and request.user.role == User.Finance:
            if required_permissions in list(permissions):
                return True
        return False


class PermissonChoices(Enum):
    NULL = 0
    LESSON_READ = 1
    LESSON_EDIT = 2
    LESSON_DELETE = 3

    SCHOOL_READ = 4
    SCHOOL_EDIT = 5
    SCHOOL_DELETE = 6

    SETTING_ADD = 7
    SETTING_EDIT = 8
    SETTING_DELETE = 9

    TERM_READ = 10
    TERM_EDIT = 11
    TERM_DELETE = 12

    FULL = 13
    TEAM_LEAD = 14
