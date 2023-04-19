from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import (
    SchoolSerializer, CreateSchoolSerializer, TermSerializer,
    ClassSerializer, LessonSerializer
)
from utils.custom_permissions import (
    HeadOfCuricullumAccess, PermissonChoices,
    ContentCreatorAccess,
)
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import School, Class, Term, Lesson
from utils.paginations import MyPaginationClass
from rest_framework import filters, viewsets
from datetime import datetime
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
            queryset = queryset.filter(phone='+' + params.get("phone"))
        if params.get("country"):
            queryset = queryset.filter(country=params.get("country"))

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
    permission_classes = (IsAuthenticated, ContentCreatorAccess,)

    def get_required_permissions(self):
        if self.request.method == "GET":
            return PermissonChoices.LESSON_READ
        elif self.request.method == "PATCH":
            return PermissonChoices.LESSON_EDIT
        else:
            return PermissonChoices.NULL

    def post(self, request):

        _class_name = request.data.pop("_class", "NA")
        _class, _ = Class.objects.get_or_create(
            name=_class_name,
            defaults={
                "start_date": datetime.today(),
                "end_date": datetime.today()
            }
        )
        # Initialize a LessonSerializer with the request data
        serializer = LessonSerializer(data=request.data)

        # Validate the request data and save the new lession if validation is successful
        serializer.is_valid(raise_exception=True)
        serializer.save(_class=_class)

        # Return a success message in the response
        response = Response(serializer.data, status=201)
        response.success_message = "Lesson Created."
        return response

    def get(seif, request, pk=None):
        queryset = Lesson.objects.all()
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


class GetLessonListAPI(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    filter_backends = (filters.SearchFilter)
    search_fields = ['id', 'name']

    def list(self, request, pk=None):
        queryset = self.queryset
        params = self.request.query_params
        if pk:
            queryset = queryset.filter(pk=pk)
        if params.get("name"):
            queryset = queryset.filter(
                name=params.get("name")
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
