from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import (
    UserSerializer, PasswordSerializer,
    AccessRequestSerializer, RoleSerializer, ActivitySerializer,
    UpdateConfigSerializer, TwoFALoginSerializer, UpdatePasswordSerializer
)
from rest_framework import permissions, status
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, CustomPermission, ActivityLog, OTP
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .custom_token import account_activation_token
from django.utils.encoding import force_bytes, force_str
from utils.hardcoded import FORGOT_PASSWORD_URL
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import logout
from utils.custom_permissions import AdminAccess
from utils.paginations import MyPaginationClass
from school.models import School
from django.utils import timezone
from django.contrib.auth import authenticate
from .utils import OTPgenerate
from utils.custom_permissions import Auth0Permission
# Create your views here.


class RegisterAPI(APIView):
    """
    This class-based view handles user registration requests.
    It expects a POST request containing user registration data.
    """

    def post(self, request):
        """
        This method handles POST requests for user registration.
        It validates the request data and saves the new user if validation is successful.

        Args:
            request (HttpRequest): The request containing user registration data.

        Returns:
            Response: An HTTP response containing a success message if the registration is successful.
        """

        # Extract data from the request
        data = request.data

        # Initialize a UserSerializer with the request data
        serializer = UserSerializer(data=data)

        # Validate the request data and save the new user if validation is successful
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # do_after_register.delay()


        # Return a success message in the response
        response = Response(serializer.data, status=200)
        response.success_message = "User Created."
        return response


# Define the LoginAPI class, inheriting from APIView
class LoginAPI(APIView):
    # Set permission classes to allow any user (even unauthenticated) to access this view
    permission_classes = (permissions.AllowAny,)

    # Define the post method to handle HTTP POST requests
    def post(self, request, format=None):
        # Deserialize the request data using the AuthTokenSerializer
        serializer = AuthTokenSerializer(data=request.data)
        # Validate the deserialized data and raise an exception if validation fails
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(User, email=request.data["username"])
        user.remember_me = int(request.data.get("remember_me", 1))
        user.save()
        if user.is_active:
            if user.is_two_factor:
                return OTPgenerate(request.data["username"], user)
            else:
                # Get the user object from the validated data
                user = serializer.validated_data['user']
                # Generate a refresh token for the user
                refresh = RefreshToken.for_user(user)
                if user.remember_me:
                    request.session.set_expiry(settings.SESSION_COOKIE_AGE)
                    request.session.modified = True
                # Prepare the response data, including user details and tokens
                data = {
                    'id': user.id,
                    'role': user.role,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'is_two_factor': user.is_two_factor,
                }
                # Return the response with the data and a 200 status code
                response = Response(data, status=200)
                response.success_message = "Login successfully."
                return response
        else:
            response = Response(status=200)
            response.error_message = "Your account is Disabled."
            return response


class LogoutAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args):
        logout(request)
        response = Response(status=200)
        response.success_message = "Logout successfully."
        return response


class RequestAccessAPI(APIView):
    # Set permission classes to allow any user to access this API
    permission_classes = (permissions.AllowAny,)
    serializer_class = AccessRequestSerializer

    def post(self, request):
        # Get the email from the request data
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            # Try to find the user with the provided email
            user = get_object_or_404(User, email=email)
            # If the user is found, send an email with a link to change the password
            subject = 'welcome,'
            html_message = FORGOT_PASSWORD_URL.format(
                name=user.first_name + ' ' + user.last_name,
                FRONTEND_IP=settings.FE_DOMAIN,
                user_id=urlsafe_base64_encode(force_bytes(user.id)),
                user_object=account_activation_token.make_token(user)
            )
            send_mail(
                subject=subject,
                message='',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
                html_message=html_message
            )
            response = Response(status=200)
            response.success_message = "Please check your email"
            return response

        # Handle any exceptions raised during the process
        except Exception:
            response = Response(status=400)
            response.error_message = "Please provide a registered email."
            return response


class PasswordChangeAPI(APIView):
    # Set the serializer class for this API view
    serializer_class = PasswordSerializer

    def post(self, request):
        # Get the data from the request
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Decode the uid from the params
        uid = force_str(urlsafe_base64_decode(serializer.validated_data["uid"]))
        try:
            # Extract the new password and its confirmation from the request data
            password = serializer.validated_data['password']
            re_password = serializer.validated_data['confirm_password']

            # Check the uid is numeric value or not.
            if uid.isnumeric():
                # Get the token from the params.
                token = serializer.validated_data['token']
                # Get the user object using the email provided in the request
                user = get_object_or_404(User, id=uid)
                # Check the token valid or not.
                if account_activation_token.check_token(user, token):
                    # Check if the new password and its confirmation match
                    if password == re_password:
                        # If the passwords match, update the user's password with the new password
                        user.password = make_password(password)
                        user.save()
                        # Return a success response
                        response = Response(status=200)
                        response.success_message = "Password changed."
                        return response

                    # If the passwords don't match, return an error response
                    response = Response(status=400)
                    response.success_message = "Password mismatched."
                    return response
                # If the token returns False.
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            # If the uid is non-numeric value.
            return Response(status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # If there's an exception (e.g. missing fields in the request data),
            # return an error response
            response = Response(status=400)
            response.error_message = str(e)
            return response


class UserRolesAPI(APIView):
    permission_classes = (AllowAny, Auth0Permission,)

    def post(self, request):
        # Initialize a CreateRoleSerializer with the request data
        serializer = RoleSerializer(data=request.data)

        # Validate the request data and save the new event if validation is successful.
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Return a success message in the response
        response = Response(serializer.data, status=200)
        response.success_message = "Role Created."
        return response

    def get(self, request):
        queryset = User.objects.all()

        params = self.request.query_params

        admin_roles = queryset.filter(role=User.Admin)
        head_of_curicullum_roles = queryset.filter(role=User.Head_of_curicullum)

        content_creator_roles = queryset.filter(role=User.Content_creator)
        finance_roles = queryset.filter(role=User.Finance)

        queryset = queryset.filter(
            role__in=[
                User.Admin, User.Head_of_curicullum,
                User.Content_creator, User.Finance
            ]
        )
        if params.get("admin"):
            queryset = admin_roles
        if params.get("head_of_curicullum"):
            queryset = head_of_curicullum_roles
        if params.get("content_creator"):
            queryset = content_creator_roles
        if params.get("finance"):
            queryset = finance_roles

        serializer = RoleSerializer(queryset, many=True)
        pagination = MyPaginationClass()
        paginated_data = pagination.paginate_queryset(
            serializer.data, request
        )
        paginated_response = pagination.get_paginated_response({
            "admin": admin_roles.count(),
            "head_of_curicullum": head_of_curicullum_roles.count(),
            "content_creater": content_creator_roles.count(),
            "finance": finance_roles.count(),
            "data": paginated_data
        }
        ).data
        response = Response(paginated_response)
        response.success_message = "data fetch Successfully."
        return response

    def patch(self, request, pk=None):
        user_instance = get_object_or_404(User, pk=pk)
        serializer = RoleSerializer(
            user_instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = Response(serializer.data, status=200)
        response.success_message = "User Updated."
        return response

    def delete(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        user.is_active = False
        user.save()
        response = Response(status=200)
        response.success_message = "User disabled Successfully."
        return response


class PermissionView(APIView):
    permission_classes = (IsAuthenticated, AdminAccess,)

    def get(self, request):

        permissions = CustomPermission.objects.all().values(
            "id", "code_name"
        ).distinct()
        response = Response(list(permissions), status=200)
        response.success_message = "Permissions"
        return response


class ActivityAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        queryset = ActivityLog.objects.all()
        activity = queryset.filter(user=request.user.id)
        print(activity, "activity")
        serializer = ActivitySerializer(activity, many=True)
        pagination = MyPaginationClass()
        paginated_data = pagination.paginate_queryset(
            serializer.data, request
        )
        paginated_response = pagination.get_paginated_response(
            paginated_data
        ).data
        response = Response(paginated_response)
        response.success_message = "Activities."
        return response


class UpdatePasswordAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        serializer = UpdatePasswordSerializer(data=request.data)

        current_password = serializer.validated_data.get('current_password')
        new_password = serializer.validated_data.get('new_password')
        re_password = serializer.validated_data.get("re_password")

        if user.check_password(current_password):
            if new_password == re_password:
                user.password = make_password(new_password)
                user.save()
                return Response('Password updated successfully.')
            return Response("Password is mismatched.", status=400)
        return Response('Current password is incorrect.', status=400)


class UpdateConfig(APIView):
    permission_classes = (IsAuthenticated,)

    def patch(self, request, pk=None):
        user = get_object_or_404(User, pk=request.user.id)
        serializer = UpdateConfigSerializer(
            user, data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = Response(serializer.data, status=200)
        response.success_message = "Updated."
        return response


class ActivityAction(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        data = {
            "is_activity_log": request.user.is_activity_log,
            "is_two_factor": request.user.is_two_factor
        }
        response = Response(data, status=200)
        response.success_message = "configs"
        return response


class DashboardAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        queryset = School.objects.all()
        users = User.objects.filter(role=User.Parent)
        students = sum(queryset.values_list('total_students', flat=True))
        teachers = sum(queryset.values_list('total_teachers', flat=True))

        response = Response({
            "schools": queryset.count(),
            "teachers": teachers,
            "parents": users.count(),
            "students": students,
        }, status=200)
        response.success_message = "School Data."
        return response


class VerifyOTP(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = TwoFALoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer._validated_data["username"]
        password = serializer._validated_data["password"]
        otp = serializer._validated_data["otp"]
        user_instance = authenticate(username=username, password=password)
        if user_instance:
            otp_instance = OTP.objects.filter(email=username).last()
            if otp_instance.expire_time < timezone.now():
                response = Response(status=400)
                response.error_message = "OTP expire"
                return response
            elif otp_instance.otp != int(otp):
                response = Response(status=400)
                response.error_message = "Invalid otp"
                return response
            else:
                otp_instance.save()

                refresh = RefreshToken.for_user(user_instance)
                if user_instance.remember_me:
                    request.session.set_expiry(settings.SESSION_COOKIE_AGE)
                    request.session.modified = True
                data = {
                    'id': user_instance.id,
                    'role': user_instance.role,
                    'email': user_instance.email,
                    'first_name': user_instance.first_name,
                    'last_name': user_instance.last_name,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
                response = Response(data, status=200)
                response.success_message = "Login successfully."
                return response
        response = Response(status=400)
        response.error_message = "Invalid username or password."
        return response
