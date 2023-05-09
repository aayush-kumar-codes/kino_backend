from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import (
    PlanSerializer, BenefitSerializer, GetPlanSerializer,
    SubscriptionSerializer, ItemSerializer, InvoiceListSerializer,
    UserUpdateSerializer, UserSerializer, ItemSerializers
)
from rest_framework.permissions import IsAuthenticated
from utils.custom_permissions import AdminAccess
from .models import (
    Plan, Benefit, Subscription, Item, Invoice, Organization
)
from django.utils.timezone import now, timedelta
from utils.paginations import MyPaginationClass
from .utils import graph_data, generate_invoice_number
from utils.helper import get_calculated_amount
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.db.models import Sum

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
        paid = queryset.filter(
            is_paid=Subscription.Paid
        ).order_by("-created_at")
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
            "paid_statistics": round((paid_last_month * 100)/queryset.count()),
            "unpaid_count": unpaid.count(),
            "uppaid_statistics": round((unpaid_last_month * 100)/queryset.count()),
            "history_count": 5,
            "history_statistics": 0.6,
        })
        response = Response(
            paginated_response,
        )
        response.success_message = "Finance data."
        return response


class GraphDataAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        params = self.request.query_params
        queryset = Subscription.objects.all()
        lists, key = graph_data(params)
        data = []
        for value in lists:
            subscription_count = queryset.filter(key[value])
            if subscription_count:
                data.append(
                    [
                        value,
                        subscription_count.filter(
                            plan__name=Plan.KAINO_PLUS
                        ).count(),
                        subscription_count.filter(
                            plan__name=Plan.KAINO_BASIC
                        ).count(),
                        subscription_count.filter(
                            plan__name=Plan.KAINO_SOCIAL
                        ).count()
                    ]
                )
            else:
                data.append(
                    [
                        value, 0, 0, 0
                    ]
                )
        return Response(data)


class InvoiceAPI(APIView):
    permission_classes = (IsAuthenticated, AdminAccess,)

    def post(self, request):
        data = request.data
        serializer = ItemSerializer(data=data)

        serializer.is_valid(raise_exception=True)

        items = serializer.validated_data["item"]
        invoice = serializer.validated_data["invoice"]

        organization = get_object_or_404(
            Organization, pk=invoice['organization']
            )

        invoice_instance, created = Invoice.objects.get_or_create(
            invoice_number=invoice.get("invoice_number"),
            defaults={
                "organization": organization,
                "po_number": invoice.get("po_number"),
                "invoice_from": invoice.get("invoice_from"),
                "invoice_to": f"{organization.name}'s {organization.address}",
                "name_of_signee": invoice.get("name_of_signee"),
                "due_date": invoice.get("due_date", str(now().date() + timedelta(days=7))),
                "status": Invoice.Draft if invoice.get("is_draft") else Invoice.Unpaid 
            }
        )
        if created:
            invoice_instance.sign_img.save(
                str(request.data.get("sign_img")),
                ContentFile(request.data.get("sign_img").read())
            )

            for item in items:
                item["invoice"] = invoice_instance
                plan = get_object_or_404(Plan, name=item.get("plan"))
                item["items"] = item.get("item_name", "Subscription")
                item["plan"] = plan
                item["price"] = plan.price
                item["amount"] = get_calculated_amount(
                    plan, item.get("quantity", 1),
                    item.get("discount")
                )
                item.pop("item_name")
                Item.objects.create(
                    **item
                )
            response = Response()
            response.success_message = "Invoice Created"
            return response
        response = Response(status=400)
        response.error_message = "Invoice already exists"
        return response

    def get(self, request):
        params = self.request.query_params
        if params.get("invoice"):
            queryset = Invoice.objects.filter(organization__name=params.get("invoice"))
        if params.get("pk"):
            queryset = Invoice.objects.filter(pk=params.get("pk"))
        serializer = ItemSerializers(queryset, many=True, context={"request": request})
        response = Response(serializer.data)
        response.success_message = "Invoice data."
        return response

    def delete(self, request, pk=None):
        invoice = get_object_or_404(Invoice, pk=pk)
        invoice.delete()
        response = Response(status=200)
        response.success_message = "Invoice Deleted Successfully."
        return response


class InvoiceListAPI(APIView):
    permission_classes = (IsAuthenticated, AdminAccess,)

    def get(self, request):
        params = self.request.query_params

        queryset = Invoice.objects.all()
        items = Item.objects.all()

        total_amount = items.aggregate(Sum('amount'))['amount__sum']
        paid_amouint = items.filter(invoice__status=Invoice.Paid)
        unpaid_amouint = items.filter(invoice__status=Invoice.Unpaid)
        overDue_amouint = items.filter(invoice__status=Invoice.Overdue)

        INVOICE_STATUS = {
            "paid": Invoice.Paid,
            "unpaid": Invoice.Unpaid,
            "overdue": Invoice.Overdue,
            "draft": Invoice.Draft,
            "recurring": Invoice.Recurring,
            "cancelled": Invoice.Cancelled,
        }
        if params.get("status"):
            queryset = queryset.filter(status=INVOICE_STATUS[params.get("status", None)])

        serializer = InvoiceListSerializer(queryset, many=True, context={"request": request})
        pagination = MyPaginationClass()
        paginated_data = pagination.paginate_queryset(
            serializer.data, request
        )
        paginated_response = pagination.get_paginated_response(
            paginated_data
        ).data
        paginated_response.update({
            "total_amount": total_amount,
            "count_total": Item.objects.count(),
            "paid_amount": paid_amouint.aggregate(Sum('amount'))['amount__sum'],
            "count_paid": paid_amouint.count(),
            "unpaid_amount": unpaid_amouint.aggregate(Sum('amount'))['amount__sum'],
            "count_unpaid": unpaid_amouint.count(),
            "overDue_amount": overDue_amouint.aggregate(Sum('amount'))['amount__sum'],
            "count_overdue": overDue_amouint.count()
        })
        response = Response(paginated_response)
        response.success_message = "List All Invoice"
        return response


class InvoicePreData(APIView):
    permission_classes = (IsAuthenticated, AdminAccess,)

    def get(self, request):
        uuid = generate_invoice_number()
        invoice_to = Organization.objects.values(
            "id", "name", "address", "city", "country"
        )
        serializer = UserSerializer(request.user)
        data = {
            "invoice_no": uuid,
            "invoice_from": serializer.data,
            "invoice_to": list(invoice_to)
        }
        response = Response(data)
        response.success_message = "Invoice Details."
        return response

    def patch(self, request):
        user = request.user
        serializer = UserUpdateSerializer(
            user, data=request.data, partial=True
        )
        response = Response(serializer.data, status=200)
        response.success_message = "User Address Updated."
        return response
