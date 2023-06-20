from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import (
    SchoolSerializer, CreateSchoolSerializer, TermSerializer,
    ClassSerializer, LessonSerializer, OrganizationSerializer,
    SchoolDashboardSerializer, ClassAndTeacher
)
from users.serializers import (
    FlnSerializer, StudentSerializer, TeacherSerializer, ParentSerializer
)
from utils.custom_permissions import (
    HeadOfCuricullumAccess, PermissonChoices,
    ContentCreatorAccess, SchoolAdminAccess
)
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import School, Class, Term, Lesson, Organization, User
from users.models import FLNImpact, Teacher, Student, Parent
from users.models import RollCall
from utils.paginations import MyPaginationClass
from rest_framework import filters, viewsets
from datetime import datetime
from django.db.models import Sum
from .utils import get_school_obj
from datetime import date, timedelta

# Create your views here.


class SchoolAPI(APIView):
    permission_classes = (IsAuthenticated, HeadOfCuricullumAccess,)

    def get_required_permissions(self):
        if self.request.method == "GET":
            return PermissonChoices.SCHOOL_READ
        elif self.request.method == "PATCH":
            return PermissonChoices.SCHOOL_EDIT
        else:
            return PermissonChoices.NULL

    def post(self, request):

        # Extract data from the request
        data = request.data

        # Initialize a CreateSchoolSerializer with the request data
        serializer = CreateSchoolSerializer(data=data)

        # Validate the request data and save the new school if validation is successful.
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Return a success message in the response
        response = Response(serializer.data, status=201)
        response.success_message = "School Created."
        return response

    def get(self, request, pk=None):
        school = get_object_or_404(School, pk=pk)
        serializer = SchoolSerializer(school, context={"request": request})
        response = Response({
            "data": serializer.data,
            "total_teachers": school.total_teachers,
        }, status=200)
        response.success_message = "School Data."
        return response

    def patch(self, request, pk=None):
        school = get_object_or_404(School, pk=pk)
        serializer = SchoolSerializer(
            school, data=request.data, context={"request": request},
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = Response(serializer.data, status=200)
        response.success_message = "School Updated."
        return response

    def delete(self, request, pk=None):
        school = get_object_or_404(School, pk=pk)
        school.delete()
        response = Response(status=200)
        response.success_message = "School Deleted Successfully."
        return response


class GetSchoolListAPI(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = School.objects.all()
    serializer_class = SchoolSerializer
    filter_backends = (filters.SearchFilter)
    search_fields = ['name', 'id', 'phone', 'country']

    def list(self, request, pk=None):
        queryset = self.queryset
        params = self.request.query_params
        if pk:
            queryset = queryset.filter(pk=pk)
        if params.get("subscription"):
            queryset = queryset.filter(
                school_subscription__plan__name=params.get("subscription")
            )
        if params.get("phone"):
            queryset = queryset.filter(phone__icontains='+' + params.get("phone"))
        if params.get("country"):
            queryset = queryset.filter(country__icontains=params.get("country"))
        if params.get("id"):
            queryset = queryset.filter(id__icontains=params.get("id"))
        if params.get("name"):
            queryset = queryset.filter(name__icontains=params.get("name"))
        if params.get("organization"):
            queryset = queryset.filter(organization__name__icontains=params.get("organization"))
        serializer = SchoolSerializer(
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
        response.success_message = "School Data."
        return response


class TermAPI(APIView):
    permission_classes = (IsAuthenticated, HeadOfCuricullumAccess,)

    def get_required_permissions(self):
        if self.request.method == "GET":
            return PermissonChoices.TERM_READ
        elif self.request.method == "PATCH":
            return PermissonChoices.TERM_EDIT
        else:
            return PermissonChoices.NULL

    def post(self, request):

        # Extract data from the request
        data = request.data

        # Initialize a TermSerializer with the request data
        serializer = TermSerializer(data=data)

        # Validate the request data and save the new term if validation is successful
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Return a success message in the response
        response = Response(serializer.data, status=201)
        response.success_message = "Term System Created."
        return response

    def get(self, request, pk=None):
        queryset = Term.objects.all()
        if pk:
            queryset = queryset.filter(pk=pk)
        serializer = TermSerializer(queryset, many=True)
        pagination = MyPaginationClass()
        paginated_data = pagination.paginate_queryset(
            serializer.data, request
        )
        paginated_response = pagination.get_paginated_response(
            paginated_data
        ).data
        response = Response(paginated_response)
        response.success_message = "Term Data."
        return response

    def patch(self, request, pk=None):
        term = get_object_or_404(Term, pk=pk)
        serializer = TermSerializer(
            term, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = Response(serializer.data, status=200)
        response.success_message = "Term System Updated."
        return response

    def delete(self, request, pk=None):
        term = get_object_or_404(Term, pk=pk)
        term.delete()
        response = Response(status=200)
        response.success_message = "Term Deleted Successfully."
        return response


class AllTermsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        queryset = Term.objects.values("id", "term_name")
        response = Response(list(queryset), status=200)
        response.success_message = "Term Data."
        return response


class ClassAPI(APIView):
    permission_classes = (IsAuthenticated,)  # give permission to schoolaccess.

    def post(self, request):

        # Initialize a TermSerializer with the request data
        serializer = ClassSerializer(data=request.data)

        # Validate the request data and save the new term if validation is successful
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Return a success message in the response
        response = Response(serializer.data, status=201)
        response.success_message = "Class Created."
        return response

    def get(seif, request, pk=None):
        queryset = Class.objects.all()
        if pk:
            queryset = queryset.filter(pk=pk)
        serializer = ClassSerializer(queryset, many=True)
        pagination = MyPaginationClass()
        paginated_data = pagination.paginate_queryset(
            serializer.data, request
        )
        paginated_response = pagination.get_paginated_response(
            paginated_data
        ).data
        response = Response(paginated_response)
        response.success_message = "Class Data."
        return response


class LessonAPI(APIView):
    permission_classes = (IsAuthenticated, SchoolAdminAccess,)

    def get_required_permissions(self):
        if self.request.method == "GET":
            return PermissonChoices.LESSON_READ
        elif self.request.method == "PATCH":
            return PermissonChoices.LESSON_EDIT
        else:
            return PermissonChoices.NULL

    def post(self, request):
        data = request.data

        school = get_school_obj(request)
        if not school:
            return Response("School not found.")

        _class_name = request.data.pop("_class", "NA")
        _class, _ = Class.objects.get_or_create(
            name=_class_name,
            defaults={
                "start_date": datetime.today(),
                "end_date": datetime.today()
            }
        )
        data["school"] = school.id
        # Initialize a LessonSerializer with the request data
        serializer = LessonSerializer(data=data)

        # Validate the request data and save the new lession if validation is successful
        serializer.is_valid(raise_exception=True)
        serializer.save(_class=_class)

        # Return a success message in the response
        response = Response(serializer.data, status=201)
        response.success_message = "Lesson Created."
        return response

    def get(seif, request, pk=None):
        school = get_school_obj(request)
        if not school:
            return Response("School not found.")
        queryset = Lesson.objects.filter(school=school.id)
        if pk:
            queryset = queryset.filter(pk=pk)
        serializer = LessonSerializer(queryset, many=True)
        pagination = MyPaginationClass()
        paginated_data = pagination.paginate_queryset(
            serializer.data, request
        )
        paginated_response = pagination.get_paginated_response(
            paginated_data
        ).data
        response = Response(paginated_response)
        response.success_message = "Lesson Data."
        return response

    def patch(self, request, pk=None):
        lesson = get_object_or_404(Lesson, pk=pk)
        _class_name = request.data.pop("_class", "NA")
        _class, _ = Class.objects.get_or_create(
            name=_class_name,
            defaults={
                "start_date": datetime.today(),
                "end_date": datetime.today()
            }
        )
        serializer = LessonSerializer(lesson, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(_class=_class)
        response = Response(serializer.data, status=200)
        response.success_message = "Lesson Updated."
        return response

    def delete(self, request, pk=None):
        lesson = get_object_or_404(Lesson, pk=pk)
        lesson.delete()
        response = Response(status=200)
        response.success_message = "Lesson Deleted Successfully."
        return response


class GetLessonListAPI(APIView):
    permission_classes = (IsAuthenticated,)
    filter_backends = (filters.SearchFilter)
    search_fields = ['id', 'name']

    def get(self, request, pk=None):
        school = get_school_obj(request)
        if not school:
            return Response("School not found.")
        queryset = Lesson.objects.filter(school=school.id)
        params = self.request.query_params
        if pk:
            queryset = queryset.filter(pk=pk)
        if params.get("name"):
            queryset = queryset.filter(
                name__icontains=params.get("name")
            )
        if params.get("class"):
            queryset = queryset.filter(
                _class__name=params.get("class")
            )

        serializer = LessonSerializer(
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
        response.success_message = "Lesson Data."
        return response


class GetOrganizationsListAPI(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    filter_backends = (filters.SearchFilter)
    search_fields = ['id', 'country']

    def list(self, request):
        queryset = self.queryset
        params = self.request.query_params
        if params.get("pk"):
            queryset = queryset.filter(pk__icontains=params.get("pk"))
        if params.get("country"):
            queryset = queryset.filter(
                country__icontains=params.get("country")
            )
        serializer = OrganizationSerializer(
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
        response.success_message = "Organizations Data."
        return response


class SchoolDashboardAPI(APIView):
    permission_classes = (IsAuthenticated, SchoolAdminAccess,)

    def get(self, request):
        impact = FLNImpact.objects.all()
        school = get_school_obj(request)
        if not school:
            return Response("School not found.")
        roll_call = RollCall.objects.filter(student__user__school_users=school)
        starting = date.today().replace(day=1)
        next_month = starting.replace(day=28) + timedelta(days=4)
        last_date = next_month - timedelta(days=next_month.day)
        month_present = roll_call.filter(
                attendance=RollCall.Present,
                date__range=(starting, last_date),
            ).count()
        month_absentees = roll_call.filter(
                attendance=RollCall.Absent,
                date__range=(starting, last_date),
            ).count()
        total = month_present + month_absentees
        if total and month_present is not None:
            percentage = (month_present * 100) / total
        else:
            percentage = 0
        lessons = Lesson.objects.filter(school=school.id)
        is_covered = lessons.filter(is_covered=True)
        serializer = FlnSerializer(impact, many=True)
        schoolserializer = SchoolDashboardSerializer(school)
        data = {
            "classes": "",
            "coverage": {
                "covered":is_covered.count(),
                "Total": lessons.count()
            },
            **schoolserializer.data,
            "summery_percentage": round(percentage),
            "present": month_present,
            "absent": month_absentees,
            "fln_over_all": impact.aggregate(Sum("numbers"))["numbers__sum"],
            "fln_impact": serializer.data
        }
        response = Response(data)
        response.success_message = "School Dashboard Data."
        return response


class LessonCoverageAPI(APIView):
    permission_classes = (IsAuthenticated, SchoolAdminAccess,)

    def get(self, request):
        school = get_school_obj(request)
        if not school:
            return Response("School not found.")
        lessons = Lesson.objects.filter(school=school.id)
        classes = lessons.values_list("_class__name").distinct()
        list_data = []
        for i in list(classes):
            is_covered = lessons.filter(_class__name=i[0], is_covered=True).count()
            _class = lessons.filter(_class__name=i[0]).count()
            class_data = {"class": i[0], "covered": is_covered, "total": _class}
            list_data.append(class_data)
        response = Response(list_data)
        response.success_message = "Coverage Data."
        return response


class ClassesAPI(APIView):
    permission_classes = (IsAuthenticated, SchoolAdminAccess,)

    def get(self, request):
        school = get_school_obj(request)
        if not school:
            return Response("School not found.")
        teachers = User.objects.filter(
            school_users=school, role=User.Teacher
        ).order_by('teacher__main_class__name')
        serializer = ClassAndTeacher(teachers, many=True)
        response = Response(serializer.data)
        response.success_message = "Classes."
        return response


class StudentDataAPI(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, SchoolAdminAccess,)
    filter_backends = (filters.SearchFilter)
    search_fields = ['id', 'name']

    def list(self, request):
        params = self.request.query_params
        school = get_school_obj(request)
        if not school:
            return Response("School not found.")
        queryset = Student.objects.filter(user__school_users=school, user__role=User.Student)
        
        if params.get("pk"):
            queryset = queryset.filter(pk=params.get("pk"))
        if params.get("name"):
            queryset = queryset.filter(user__first_name__icontains=params.get("name"))
        if params.get("phone"):
            queryset = queryset.filter(user__mobile_no__icontains='+' + params.get("phone"))
        if params.get("gender"):
            queryset = queryset.filter(user__gender=params.get("gender"))
        if params.get("class"):
            queryset = queryset.filter(_class__name=params.get("class"))

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


class ParentDataAPI(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, SchoolAdminAccess,)
    filter_backends = (filters.SearchFilter)
    search_fields = ['id', 'name']

    def list(self, request):
        params = self.request.query_params
        school = get_school_obj(request)
        if not school:
            return Response("School not found.")
        queryset = Parent.objects.filter(user__school_users=school)

        if params.get("pk"):
            queryset = queryset.filter(pk=params.get("pk"))
        if params.get("name"):
            queryset = queryset.filter(user__first_name__icontains=params.get("name"))
        if params.get("phone"):
            queryset = queryset.filter(user__mobile_no__icontains='+' + params.get("phone"))
        if params.get("class"):
            queryset = queryset.filter(student_parent___class__name=params.get("class"))

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


class TeacherDataAPI(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, SchoolAdminAccess,)
    filter_backends = (filters.SearchFilter)
    search_fields = ['id', 'name']

    def list(self, request):
        params = self.request.query_params
        school = get_school_obj(request)
        if not school:
            return Response("School not found.")
        queryset = Teacher.objects.filter(user__school_users=school, user__role=User.Teacher)

        if params.get("pk"):
            queryset = queryset.filter(pk=params.get("pk"))
        if params.get("name"):
            queryset = queryset.filter(first_name__icontains=params.get("name"))
        if params.get("class"):
            queryset = queryset.filter(main_class__name=params.get("class"))

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


class SchoolDetailsAPI(APIView):
    permission_classes = (IsAuthenticated, SchoolAdminAccess,)

    def get(self, request):
        school = get_school_obj(request)
        if school is None:
            return Response("School not found.")
        serializer = SchoolSerializer(school, context={"request": request})
        response = Response(serializer.data, status=200)
        response.success_message = "School Data."
        return response

    def patch(self, request):
        school = get_school_obj(request)
        if school is None:
            return Response("School not found.")
        try:
            serializer = SchoolSerializer(
                school, data=request.data, context={"request": request},
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = Response(serializer.data, status=200)
            response.success_message = "School Updated."
            return response
        except Exception as e:
            response = Response(status=400)
            response.error_message = str(e)
            return response
