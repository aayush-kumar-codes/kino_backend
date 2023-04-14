from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import (
    SchoolSerializer, CreateSchoolSerializer, TermSerializer
)
from utils.custom_permissions import (
    AdminAccess, HeadOfCuricullumAccess
)
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import School, User, Term
from utils.paginations import MyPaginationClass
from rest_framework import filters, viewsets

# Create your views here.


class CreateSchoolAPI(APIView):
    permission_classes = [IsAuthenticated, AdminAccess]

    def post(self, request):

        # Extract data from the request
        data = request.data

        # Initialize a SchoolSerializer with the request data
        serializer = CreateSchoolSerializer(data=data)

        # Validate the request data and save the new school if validation is successful.
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Return a success message in the response
        response = Response(serializer.data, status=201)
        response.success_message = "School Created."
        return response

    def get(self, request, pk=None):
        try:
            school = School.objects.get(id=pk)
            teachers = school.users.filter(role=User.Teacher)
            students = school.users.filter(role=User.Student)
            print(teachers.count(), students.count())
            serializer = SchoolSerializer(school)
            response = Response({
                "data": serializer.data,
                "total_teachers": teachers.count(),
            }, status=200)
            response.success_message = "School Data."
            return response
        except Exception:
            response = Response(status=400)
            response.error_message = "School Data not found."
            return response

    def patch(self, request, pk=None):
        try:
            data = School.objects.get(pk=pk)
            serializer = SchoolSerializer(data, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = Response(serializer.data, status=200)
            response.success_message = "School Updated."
            return response
        except Exception:
            response = Response(status=400)
            response.error_message = "School Data not found."
            return response

    def delete(self, request, pk=None):
        try:
            school = get_object_or_404(School, pk=pk)
            school.delete()
            response = Response(status=200)
            response.success_message = "School Deleted Successfully."
            return response
        except Exception:
            response = Response(status=400)
            response.error_message = "School Data not found."
            return response


# Access by only School Head of Curricullum
class SchoolHeadAccess(APIView):
    permission_classes = [IsAuthenticated, HeadOfCuricullumAccess]

    def get(self, request, pk=None):
        try:
            school = School.objects.get(id=pk)
            teachers = school.users.filter(role=User.Teacher)
            students = school.users.filter(role=User.Student)
            print(teachers.count(), students.count())
            serializer = SchoolSerializer(school)
            response = Response({
                "data": serializer.data,
                "total_teachers": teachers.count(),
            }, status=200)
            response.success_message = "School Data."
            return response
        except Exception:
            response = Response(status=400)
            response.error_message = "School Data not found."
            return response

    def patch(self, request, pk=None):
        try:
            data = School.objects.get(pk=pk)
            serializer = SchoolSerializer(data, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            response = Response(serializer.data, status=200)
            response.success_message = "School Updated."
            return response
        except Exception:
            response = Response(status=400)
            response.error_message = "School Data not found."
            return response


class GetSchoolListAPI(viewsets.ModelViewSet):
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


class CreateTermAPI(APIView):
    permission_classes = [IsAuthenticated, AdminAccess]

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
        data = get_object_or_404(Term, pk=pk)
        serializer = TermSerializer(data, data=request.data)
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


class GetAllTermsAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        queryset = Term.objects.values_list('term_name', flat=True)
        response = Response(list(queryset), status=200)
        response.success_message = "Term Data."
        return response


class TermHeadAccess(APIView):
    permission_classes = (IsAuthenticated, HeadOfCuricullumAccess,)

    def get(self, request, pk=None):
        term = get_object_or_404(Term, pk=pk)
        serializer = TermSerializer(term)
        response = Response(serializer.data, status=200)
        response.success_message = "Term Data."
        return response

    def patch(self, request, pk=None):
        data = get_object_or_404(Term, pk=pk)
        serializer = TermSerializer(data, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = Response(serializer.data, status=200)
        response.success_message = "Term System Updated."
        return response
