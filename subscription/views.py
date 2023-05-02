from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import (
    PlanSerializer, BenefitSerializer, GetPlanSerializer,
    InvoiceSerializer, SubscriptionSerializer
)
from rest_framework.permissions import IsAuthenticated
from utils.custom_permissions import AdminAccess
from .models import Plan, Benefit, Subscription
from django.utils.timezone import now, timedelta
from utils.paginations import MyPaginationClass

# Create your views here.


class CreatePlanAPI(APIView):
    permission_classes = (IsAuthenticated, AdminAccess,)

    def post(self, request):

        # Extract data from the request
        data = request.data

        # Initialize a PlanSerializer with the request data
        serializer = PlanSerializer(data=data)

        # Validate the request data and save the new school if validation is successful.
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Return a success message in the response
        response = Response(serializer.data, status=201)
        response.success_message = "Plan Created."
        return response


class CreateBenefitAPI(APIView):
    permission_classes = (IsAuthenticated, AdminAccess,)

    def post(self, request):

        # Extract data from the request
        data = request.data

        # Initialize a BenefitSerializer with the request data
        serializer = BenefitSerializer(data=data)

        # Validate the request data and save the new school if validation is successful.
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Return a success message in the response
        response = Response(serializer.data, status=201)
        response.success_message = "Benefit Created."
        return response


class GetPlan(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        plan = Plan.objects.all()
        benefit = Benefit.objects.all()
        plans = GetPlanSerializer(plan, many=True)
        benefits = BenefitSerializer(benefit, many=True)
        response_data = {
            'KAINO PACKAGES': plans.data,
            'BENEFITS': benefits.data
        }
        return Response(response_data)


class FinanceAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        queryset = Subscription.objects.all()
        school = queryset.values_list("school")
        paid = queryset.filter(is_paid=Subscription.Paid).order_by("-created_at")
        unpaid = queryset.filter(is_paid=Subscription.Unpaid)
        school_added_last_month = queryset.filter(
            created_at__gte=now() - timedelta(days=30)
        )
        paid_last_month = queryset.filter(
            created_at__gte=now() - timedelta(days=30), is_paid=Subscription.Paid
        ).count()
        unpaid_last_month = queryset.filter(
            created_at__gte=now() - timedelta(days=30), is_paid=Subscription.Unpaid
        ).count()
        serializer = SubscriptionSerializer(paid, many=True)
        pagination = MyPaginationClass()
        paginated_data = pagination.paginate_queryset(
            serializer.data, request
        )
        paginated_response = pagination.get_paginated_response(
            paginated_data

        ).data
        paginated_response.update({
            "school_count": school.count(),
            "school_statistics": school_added_last_month.count(),
            "paid_count": paid.count(),
            "paid_statistics": (paid_last_month * 100)/queryset.count(),
            "unpaid_count": unpaid.count(),
            "uppaid_statistics": (unpaid_last_month * 100)/queryset.count(),
            "history_count": 5,
            "history_statistics": 0.6,
        })
        response = Response(
            paginated_response,
        )
        response.success_message = "Finance data."
        return response
