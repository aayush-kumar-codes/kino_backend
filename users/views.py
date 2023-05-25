from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import (
    UserSerializer, PasswordSerializer,
    AccessRequestSerializer, RoleSerializer, ActivitySerializer,
    UpdateConfigSerializer, TwoFALoginSerializer, UpdatePasswordSerializer,
    ParentSerializer, TeacherSerializer, StudentSerializer, FlnSerializer,
    GetAllParentSerializer, CreateMemberSerializer, RollCallSerializer
)
from rest_framework import permissions, status
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import (
    User, CustomPermission, ActivityLog, OTP, Parent, Teacher, Student,
    FLNImpact, RollCall
)
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .custom_token import account_activation_token
from django.utils.encoding import force_bytes, force_str
from utils.hardcoded import FORGOT_PASSWORD_URL, LOGIN_ALART
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import logout
from utils.custom_permissions import AdminAccess, SchoolAdminAccess
from utils.paginations import MyPaginationClass
from school.models import School, Organization, Class
from django.utils import timezone
from django.contrib.auth import authenticate
from .utils import OTPgenerate, graph_data
from rest_framework import filters, viewsets
from django.db.models import Sum
from subscription.models import Item, Invoice, Subscription
from django.core.files.base import ContentFile
from school.utils import get_school_obj
from datetime import date, timedelta

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
                token = RefreshToken.for_user(user)
                access_token = token.access_token
                access_token["role"] = user.role
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
                    'refresh': str(token),
                    'access': str(access_token),
                    'is_two_factor': user.is_two_factor,
                }
                # Return the response with the data and a 200 status code
                response = Response(data, status=200)
                if user.is_activity_log:
                    ActivityLog.create_activity_log(request, user, LOGIN_ALART)
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
    permission_classes = (IsAuthenticated, AdminAccess,)

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

        serializer = RoleSerializer(queryset.exclude(id=request.user.id), many=True)
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
        impact = FLNImpact.objects.all()
        queryset = School.objects.all()
        users = User.objects.filter(role=User.Parent)
        organizations = Organization.objects.all()
        students = sum(queryset.values_list('total_students', flat=True))
        teachers = sum(queryset.values_list('total_teachers', flat=True))

        top_orgs = organizations.annotate(
            total_students=Sum('organization__total_students')*100 / students
        ).values('name', 'total_students').order_by("-total_students")[:4]

        items = Item.objects.all()
        paid = items.filter(invoice__status=Invoice.Paid).aggregate(Sum('amount'))['amount__sum'],
        due = items.filter(invoice__status=Invoice.Due).aggregate(Sum('amount'))['amount__sum'],
        school = queryset.filter(school_subscription__is_paid=Subscription.Paid).count()
        serializer = FlnSerializer(impact, many=True)

        response = Response({
            "schools": queryset.count(),
            "teachers": teachers,
            "parents": users.count(),
            "students": students,
            "organizations": {
                "total": organizations.count(),
                "data": list(top_orgs)
            },
            "paid_data": {
                "schools_paid": school,
                "amount_paid": paid,
                "amount_due": due
            },
            "fln_over_all": impact.aggregate(Sum("numbers"))["numbers__sum"],
            "fln_impact": serializer.data
        }, status=200)
        response.success_message = "Admin Dashboard Data."
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

                token = RefreshToken.for_user(user_instance)
                access_token = token.access_token
                access_token["role"] = user_instance.role
                if user_instance.remember_me:
                    request.session.set_expiry(settings.SESSION_COOKIE_AGE)
                    request.session.modified = True
                data = {
                    'id': user_instance.id,
                    'role': user_instance.role,
                    'email': user_instance.email,
                    'first_name': user_instance.first_name,
                    'last_name': user_instance.last_name,
                    'refresh': str(token),
                    'access': str(access_token),
                    'is_two_factor': user_instance.is_two_factor,
                }
                response = Response(data, status=200)
                if user_instance.is_activity_log:
                    message = "You login through two-factor auth."
                    ActivityLog.create_activity_log(request, user_instance, message)
                response.success_message = "Login successfully."
                return response
        response = Response(status=400)
        response.error_message = "Invalid username or password."
        return response


class ParentAPI(APIView):
    permission_classes = (IsAuthenticated, SchoolAdminAccess,)

    def post(self, request):
        school = get_school_obj(request)
        data = request.data
        serializer = CreateMemberSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        parent = serializer.validated_data["member"]
        try:
            user_instance, created = User.objects.get_or_create(
                email=user.get("email"),
                defaults={
                    "username": user.get("username"),
                    "first_name": user.get("first_name"),
                    "last_name": user.get("last_name"),
                    "gender": user.get("gender"),
                    "dob": user.get("dob"),
                    "role": User.Parent,
                    "mobile_no": user.get("mobile_no"),
                }
            )

            if created:
                password = user.get("password")
                profile_img = data.get("profile_img", None)
                if password:
                    user_instance.set_password(password)

                if profile_img:
                    user_instance.profile_img.save(
                        str(profile_img),
                        ContentFile(profile_img.read())
                    )

            Parent.objects.create(
                user=user_instance,
                occupation=parent.get("occupation"),
                nin=parent.get("nin"),
                address=parent.get("address"),
                city=parent.get("city"),
                region=parent.get("region"),
                country=parent.get("country"),
            )
            school.users.add(user_instance)
        except Exception as e:
            response = Response(str(e), status=400)
            response.error_message = str(e)
            return response

        response = Response(status=200)
        response.success_message = "Parent Created."
        return response

class GetParentListAPI(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Parent.objects.all()
    serializer_class = ParentSerializer
    filter_backends = (filters.SearchFilter)
    search_fields = ['id', 'phone']

    def list(self, request, pk=None):
        queryset = self.queryset
        params = self.request.query_params
        if pk:
            queryset = queryset.filter(pk=pk)
        if params.get("country"):
            queryset = queryset.filter(country=params.get("country"))
        if params.get("name"):
            queryset = queryset.filter(user__first_name=params.get("name"))

        serializer = ParentSerializer(
            queryset, many=True, context={"request": request}
        )
        pagination = MyPaginationClass()
        paginated_data = pagination.paginate_queryset(
            serializer.data, request
        )
        paginated_response = pagination.get_paginated_response(
            paginated_data
        ).data
        response = Response(paginated_response)
        response.success_message = "Parent Data."
        return response


class ClassBasedParentCount(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        school = get_school_obj(request)
        if not school:
            return Response("School not found.")
        queryset = Parent.objects.filter(user__school_users=school)
        classes = queryset.values_list("student_parent___class__name").distinct()
        dict = {}
        for i in list(classes):
            parents = queryset.filter(student_parent___class__name=i[0]).count()
            dict[i[0]] = parents
        dict.pop(None)
        response = Response(dict, status=200)
        response.success_message = "countend data."
        return response


class TeacherAPI(APIView):
    permission_classes = (IsAuthenticated, SchoolAdminAccess,)

    def post(self, request):
        school = get_school_obj(request)
        data = request.data
        serializer = CreateMemberSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        teacher = serializer.validated_data["member"]
        try:
            user_instance, created = User.objects.get_or_create(
                email=user.get("email"),
                defaults={
                    "username": user.get("username"),
                    "first_name": user.get("first_name"),
                    "last_name": user.get("last_name"),
                    "gender": user.get("gender"),
                    "dob": user.get("dob"),
                    "role": User.Teacher,
                    "mobile_no": user.get("mobile_no"),
                }
            )

            if created:
                password = user.get("password")
                profile_img = data.get("profile_img", None)
                if password:
                    user_instance.set_password(password)

                if profile_img:
                    user_instance.profile_img.save(
                        str(profile_img),
                        ContentFile(profile_img.read())
                    )

            main_class = Class.objects.get(pk=teacher.get("main_class_id"))
            Teacher.objects.create(
                user=user_instance,
                teacher_id=teacher.get("teacher_id"),
                joining_date=teacher.get("joining_date"),
                year_of_experience=teacher.get("year_of_experience"),
                qualification=teacher.get("qualification"),
                main_class = main_class,
                teacher_role = teacher.get("role"),
                address = teacher.get("address"),
                city=teacher.get("city"),
                region=teacher.get("region"),
                country=teacher.get("country"),
            )
            school.users.add(user_instance)
        except Exception as e:
            response = Response(status=400)
            response.error_message = str(e)
            return response
        response = Response(status=200)
        response.success_message = "Teacher Created."
        return response


class GetTeacherListAPI(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    filter_backends = (filters.SearchFilter)
    search_fields = ['id', 'name']

    def list(self, request, pk=None):
        queryset = self.queryset
        params = self.request.query_params

        if pk:
            queryset = queryset.filter(pk=pk)
        if params.get("name"):
            queryset = queryset.filter(user__first_name=params.get("name"))
        if params.get("class"):
            queryset = queryset.filter(main_class__name=params.get("class"))
        if params.get("country"):
            queryset = queryset.filter(country=params.get("country"))

        serializer = TeacherSerializer(
            queryset, many=True, context={"request": request}
        )
        pagination = MyPaginationClass()
        paginated_data = pagination.paginate_queryset(
            serializer.data, request
        )
        paginated_response = pagination.get_paginated_response(
            paginated_data
        ).data
        response = Response(paginated_response)
        response.success_message = "Teacher Data."
        return response


class GetAllParentsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        queryset = Parent.objects.all()
        serializer = GetAllParentSerializer(queryset, many=True)
        response = Response(serializer.data)
        response.success_message = "All Parents."
        return response


class StudentAPI(APIView):
    permission_classes = (IsAuthenticated, SchoolAdminAccess,)

    def post(self, request):
        school = get_school_obj(request)
        data = request.data
        serializer = CreateMemberSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        student = serializer.validated_data["member"]
        try:
            if student.get("parents_id") is not None:
                parent = Parent.objects.get(pk=student.get("parents_id"))
            else:
                parent = None
            user_instance, created = User.objects.get_or_create(
                email=user.get("email"),
                defaults={
                    "username": user.get("email"),
                    "first_name": user.get("first_name"),
                    "last_name": user.get("last_name"),
                    "gender": user.get("gender"),
                    "dob": user.get("dob"),
                    "mobile_no": user.get("mobile_no"),
                    "role": User.Student,
                    "is_active": False,
                }
            )
            if created:
                profile_img = data.get("profile_img", None)
                if profile_img:
                    user_instance.profile_img.save(
                        str(profile_img),
                        ContentFile(profile_img.read())
                    )
            parent_id = student.get("parents_id")
            parent = Parent.objects.get(pk=parent_id) if parent_id is not None else None
            class_id = Class.objects.get(id=student.get("class_id"))

            Student.objects.create(
                user=user_instance,
                parent=parent,
                religion=student.get("religion"),
                id_no=student.get("id_no"),
                _class=class_id,
                address=student.get("address"),
            )
            school.users.add(user_instance)
        except Exception as e:
            response = Response(status=400)
            response.error_message = str(e)
            return response
        response = Response(status=200)
        response.success_message = "Student Created."
        return response


class GetStudentListAPI(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    filter_backends = (filters.SearchFilter)
    search_fields = ['id', 'name']

    def list(self, request, pk=None):
        queryset = self.queryset
        params = self.request.query_params

        if pk:
            queryset = queryset.filter(pk=pk)
        if params.get("name"):
            queryset = queryset.filter(user__first_name=params.get("name"))
        if params.get("class"):
            queryset = queryset.filter(main_class__name=params.get("class"))
        if params.get("gender"):
            queryset = queryset.filter(user__gender=params.get("gender"))
        if params.get("id_no"):
            queryset = queryset.filter(id_no=params.get("id_no"))
        if params.get("country"):
            queryset = queryset.filter(country=params.get("country"))
        serializer = StudentSerializer(
            queryset, many=True, context={"request": request}
        )
        pagination = MyPaginationClass()
        paginated_data = pagination.paginate_queryset(
            serializer.data, request
        )
        paginated_response = pagination.get_paginated_response(
            paginated_data
        ).data
        response = Response(paginated_response)
        response.success_message = "Student Data."
        return response


class ClassBasedStudentCount(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        school = get_school_obj(request)
        if not school:
            return Response("School not found.")
        queryset = User.objects.filter(school_users=school, role=User.Student)
        classes = queryset.values_list("student___class__name").distinct()
        dict = {}
        for i in list(classes):
            students = queryset.filter(student___class__name=i[0]).count()
            dict[i[0]] = students
        response = Response(dict, status=200)
        response.success_message = "countend data."
        return response


class RollCallAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        params = self.request.query_params
        school = get_school_obj(request)
        if not school:
            return Response("School not found.")

        queryset = RollCall.objects.filter(student__user__school_users=school)

        total_attendance = queryset.filter(attendance=RollCall.Present).count()
        total_absent = queryset.filter(attendance=RollCall.Absent).count()
        total_students = school.users.filter(role=User.Student).count()

        if params.get("class"):
            queryset = queryset.filter(student___class__name=params.get("class"))
        if params.get("date"):
            queryset = queryset.filter(date=params.get("date"))
        if params.get("year"):
            queryset = queryset.filter(date__year=params.get("year"))

        serializer = RollCallSerializer(
            queryset, many=True, context={"request": request}
            )
        pagination = MyPaginationClass()
        data = {
            "total_students": total_students,
            "total_attendance": total_attendance,
            "total_absent": total_absent
        }
        paginated_data = pagination.paginate_queryset(
            serializer.data, request
        )
        paginated_response = pagination.get_paginated_response(
            paginated_data
        ).data
        paginated_response.update(data)
        response = Response(paginated_response)
        response.success_message = "Roll-call Data."
        return response


class RollCallBarGraphAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        params = self.request.query_params
        school = get_school_obj(request)
        if not school:
            return Response("School not found.")
        queryset = RollCall.objects.filter(student__user__school_users=school)
        lists, key = graph_data(params)
        data = []
        for value in lists:
            roll_call_count = queryset.filter(key[value])
            if roll_call_count:
                data.append(
                    [
                        value,
                        roll_call_count.filter(attendance=RollCall.Present).count(),
                        roll_call_count.filter(attendance=RollCall.Absent).count(),
                        roll_call_count.filter(attendance=RollCall.Excuse).count(),
                    ]
                )
            else:
                data.append(
                    [
                        value, 0, 0, 0
                    ]
                )
        return Response(data)


class RollCallPieChartAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        params = self.request.query_params
        interval = params.get('interval')
        school = get_school_obj(request)
        if not school:
            return Response("School not found.")
        roll_call = RollCall.objects.filter(student__user__school_users=school)

        if interval == 'weekly':
            start_date = date.today() - timedelta(days=date.today().weekday())
            end_date = start_date + timedelta(days=6)
        elif interval == 'monthly':
            start_date = date.today().replace(day=1)
            next_month = start_date.replace(day=28) + timedelta(days=4)
            end_date = next_month - timedelta(days=next_month.day)
        else:
            start_date = date.today()
            end_date = start_date
        
        _class = roll_call.values_list("student___class__name").distinct()
        list_data = []
        for i in list(_class):
            queryset = roll_call.filter(
                attendance=RollCall.Absent,
                date__range=(start_date, end_date),
                student___class__name=i[0]
            ).count()
            list_data.append(
                [
                    i[0], queryset
                ]
            )
        starting = date.today().replace(day=1)
        next_month = starting.replace(day=28) + timedelta(days=4)
        last_date = next_month - timedelta(days=next_month.day)
        month_absentees = roll_call.filter(
                attendance=RollCall.Absent,
                date__range=(starting, last_date),
            ).count()
        data = {
            "list_data": list_data,
            "most_absentees": month_absentees
        }
        response = Response(data)
        response.success_message = "Pie Data."
        return response
