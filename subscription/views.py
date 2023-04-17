from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import PlanSerializer, BenefitSerializer, GetPlanSerializer
from rest_framework.permissions import IsAuthenticated
from utils.custom_permissions import AdminAccess
from .models import Plan, Benefit
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
