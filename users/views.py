from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import (
    UserSerializer, PasswordSerializer,
    AccessRequestSerializer
)
from rest_framework import permissions, status
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .custom_token import account_activation_token
from django.utils.encoding import force_bytes, force_str
from utils.hardcoded import FORGOT_PASSWORD_URL
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import logout

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

        # Return a success message in the response
        response = Response(serializer.data, status=201)
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
        # Get the user object from the validated data
        user = serializer.validated_data['user']
        # Generate a refresh token for the user
        refresh = RefreshToken.for_user(user)

        # Prepare the response data, including user details and tokens
        data = {
            'id': user.id,
            'role': user.role,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        # Return the response with the data and a 200 status code
        response = Response(data, status=200)
        response.success_message = "Login successfully."
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
