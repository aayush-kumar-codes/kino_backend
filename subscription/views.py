from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import (
    PlanSerializer, BenefitSerializer, GetPlanSerializer,
    SubscriptionSerializer, ItemSerializer, InvoiceListSerializer,
    UserSerializer, ItemSerializers,
    SchoolSubscriptionSerializer, SchoolPaymentHistorySerializer
)
from rest_framework.permissions import IsAuthenticated
from utils.custom_permissions import AdminAccess
from .models import (
    Plan, Benefit, Subscription, Item, Invoice, Organization
)
from django.utils.timezone import now, timedelta
from utils.paginations import MyPaginationClass
from .utils import graph_data, generate_invoice_number
from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from django.db.models import Sum
from school.utils import get_school_obj
from users.serializers import AccountSerializer, Address, AddressSerializer
from rave_python.rave_exceptions import TransactionVerificationError
from rave_python import RaveExceptions
from rave_python import Rave
from dotenv import load_dotenv
import os, json
from django.http import HttpResponse
from .utils import update_invoice, update_subscription


load_dotenv()
PublicKey = os.getenv("PUBLIC_KEY")
SecretKey = os.getenv("RAVE_SECRET_KEY")

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
        items = Item.objects.all()
        history = items.aggregate(Sum('amount'))['amount__sum']
        history_static = items.filter(invoice__created_date__gte=now() - timedelta(days=30)).count()

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
            "history_count": history,
            "history_statistics": round((history_static * 100 / items.count())),
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
                "status": Invoice.Draft if invoice.get("is_draft") else Invoice.Unpaid,
            }
        )
        if created:
            sign_img = data.get("sign_img", None)
            if sign_img:
                invoice_instance.sign_img.save(
                    str(sign_img),
                    ContentFile(sign_img.read())
                )
            item_list = []
            for item in items:
                item["invoice"] = invoice_instance
                plan = get_object_or_404(Plan, name=item.get("plan"))
                item["items"] = item.get("item_name", "Subscription")
                item["plan"] = plan
                item["price"] = plan.price
                item.pop("item_name")
                discount_amount = (plan.price * item.get("quantity")) * item.get("discount") / 100
                item["amount"] = (plan.price * item.get("quantity")) - discount_amount
                item_list.append(
                    Item(**item)
                )
            Item.objects.bulk_create(
                item_list
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

    def patch(self, request, pk=None):
        invoice_obj = get_object_or_404(Invoice ,pk=pk)
        serializer = ItemSerializer(
            invoice_obj, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        items = serializer.validated_data["item"]
        invoice = serializer.validated_data["invoice"]
        organization = get_object_or_404(
            Organization, pk=invoice['organization']
            )
        invoice_instance, created = Invoice.objects.update_or_create(
            invoice_number=invoice.get("invoice_number"),
            defaults={
                "organization": organization,
                "po_number": invoice.get("po_number"),
                "invoice_from": invoice.get("invoice_from"),
                "invoice_to": f"{organization.name}'s {organization.address}",
                "name_of_signee": invoice.get("name_of_signee"),
                "due_date": invoice.get("due_date", str(now().date() + timedelta(days=7))),
                "status": Invoice.Draft if invoice.get("is_draft") else Invoice.Unpaid,
            }  
        )

        item_list = []
        invoice_instance.invoice_amount.all().delete()
        for item in items:
            item["invoice"] = invoice_instance
            plan = get_object_or_404(Plan, name=item.get("plan"))
            item["items"] = item.get("item_name", "Subscription")
            item["plan"] = plan
            item["price"] = plan.price
            item.pop("item_name")
            item_list.append(
                Item(**item)
            )
        Item.objects.bulk_create(
            item_list
        )
        response = Response()
        response.success_message = "Invoice Updated."
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
            "invoice_number": uuid,
            "invoice_from": serializer.data,
            "invoice_to": list(invoice_to)
        }
        response = Response(data)
        response.success_message = "Invoice Details."
        return response

    def patch(self, request):
        user = request.user
        serializer = AddressSerializer(
            user, data=request.data, partial=True
        )
        response = Response(serializer.data, status=200)
        response.success_message = "User Address Updated."
        return response


class SchoolSubscriptionAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        school = get_school_obj(request)
        if not school:
            return Response("School not found.")
        try:
            subscription = Subscription.objects.get(school=school.id)
            if subscription.is_active:
                serializer = SchoolSubscriptionSerializer(subscription)
                response = Response(serializer.data)
                response.success_message = "Subscription data."
                return response
            response = Response(status=400)
            response.error_message = "Subscription is not activate."
            return response
        except Exception as e:
            response = Response(status=400)
            response.error_message = "You have no any Subscription."
            return response


class AccountPersonalAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        serializer = AccountSerializer(user)
        response = Response(serializer.data)
        response.success_message = "user data."
        return response

    def patch(self, request):
        user = request.user
        serializer = AccountSerializer(
            user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if 'address' in request.data:
            address_data = request.data['address']
            address_data["user"] = request.user.id
            Address.objects.update_or_create(
                user = request.user.id,
                defaults={
                    'street': address_data["street"],
                    "city": address_data["city"],
                    "district": address_data["district"],
                    "region": address_data["region"],
                    "zip_code": address_data["zip_code"],
                    "country": address_data["country"]
                },
            )
        response = Response(status=200)
        response.success_message = "User profile updated."
        return response


class SchoolPaymentHistoryAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        school = get_school_obj(request)
        if not school:
            return Response("School not found.")
        queryset = Subscription.objects.filter(school=school.id)
        serializer = SchoolPaymentHistorySerializer(queryset, many=True)
        pagination = MyPaginationClass()
        paginated_data = pagination.paginate_queryset(
            serializer.data, request
        )
        paginated_response = pagination.get_paginated_response(
            paginated_data
        ).data
        response = Response(paginated_response)
        response.success_message = "Payment History."
        return response


class SchoolInvoiceAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        params = self.request.query_params
        school = get_school_obj(request)
        if not school:
            return Response("School not found.")
        if not params.get("pk"):
            return Response("pk is missing in params.")
        queryset = Invoice.objects.filter(
            organization__organization=school, pk=params.get("pk")
        )
        serializer = ItemSerializers(
            queryset, many=True, context={"request": request}
        )
        response = Response(serializer.data)
        response.success_message = "School invoice."
        return response


class SchoolCancelPlanAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request):
        school = get_school_obj(request)
        if not school:
            return Response("School not found.")
        subscription = get_object_or_404(Subscription, school=school.id)
        subscription.is_active = False
        subscription.save()
        response = Response(status=200)
        response.success_message = "School Subscription cancelled successfully."
        return response


class FlutterwavePlanAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        rave = Rave(PublicKey, SecretKey, production=False, usingEnv=True)
        plans = rave.PaymentPlan.all()
        payment_plans = plans['returnedData']['data']['paymentplans']
        result = [{
            'id': plan['id'], 'name': plan['name'], 'amount': plan['amount'],
            'interval': plan['interval'], "status": plan["status"],
            "currency": plan["currency"]
        } for plan in payment_plans]
        response = Response(result)
        response.success_message = "Flutterwave Plans."
        return response


class CardPaymentView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        school = get_school_obj(request)
        invoice_no = Invoice.objects.get(organization__organization=school)
        rave = Rave(PublicKey, SecretKey, production=False, usingEnv=True)
        txRef = f"{invoice_no.invoice_number}/{school.id}"
        payload = {
            "cardno": request.data.get('cardno'),
            "cvv": request.data.get('cvv'),
            "expirymonth": request.data.get('expirymonth'),
            "expiryyear": request.data.get('expiryyear'),
            "currency": request.data.get('currency'),
            "country": request.data.get('country'),
            "amount": request.data.get('amount'),
            "email": request.data.get('email'),
            "phonenumber": request.data.get('phonenumber'),
            "firstname": request.data.get('firstname'),
            "lastname": request.data.get('lastname'),
            "IP": request.data.get('IP'),
            "txRef": txRef,
            "payment_plan": request.data.get("plan_id"),
            "meta": {
                "authorization": {
                    "invoice_no": invoice_no.invoice_number,
                    "school_instance": school.id,
                }
            }
        }
        try:
            response = rave.Card.charge(payload)
            if response['validationRequired']:
                if response['suggestedAuth'] is None:
                    auth_url = response['authUrl']
                    # return HttpResponse(status=302, headers={'Location': auth_url})
                    return Response({"status": "success", "message": "Payment successful", "data": response})
                else:
                    if response['suggestedAuth'] == "otp":
                        auth_url = response['authUrl']
                        return HttpResponse(status=302, headers={'Location': auth_url})
                    if response['suggestedAuth'] == 'PIN':
                        pin_payload = {
                            "PBFPubKey": PublicKey,
                            "transaction_reference": response['txRef'],
                            "PIN": request.data.get("pin")
                        }

                        pin_response = rave.Card.validate_pin(pin_payload)
                        return pin_response
            else:
                return Response({"status": "error", "message": response["message"]})
        except RaveExceptions.CardChargeError as e:
            print(e.err["errMsg"])
            print(e.err["flwRef"])
            response = ""
            return Response(e.err["errMsg"])


class MobilePaymentView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        school = get_school_obj(request)
        invoice_no = Invoice.objects.get(organization__organization=school)
        rave = Rave(PublicKey, SecretKey, production=False, usingEnv=True)
        txRef = f"{invoice_no.invoice_number}/{school.id}"
        payload = {
            "phonenumber": request.data.get("phonenumber"),
            "email": request.data.get("email"),
            "amount": request.data.get("amount"),
            "IP": request.data.get("IP"),
            "txRef": txRef,
        }
        response = rave.UGMobile.charge(payload)
        return Response(response)


class WebhookAPI(APIView):
    def post(self, request):
        secret_hash = os.getenv("RAVE_SECRET_KEY")
        signature = request.headers.get("verifi-hash")
        print(secret_hash, signature, "rrrrrrrr")
        # if signature == None or (signature != secret_hash):
        #     # This request isn't from Flutterwave; discard
        #     return HttpResponse(status=401)
        payload = request.body
        print(payload, "qwerty")
        response_str = payload.decode('utf-8')
        payload = json.loads(response_str)
        self.payment_verify(payload)
        return Response(status=200)

    def payment_verify(self, payload):
        school_id = payload["data"]["tx_ref"].split("/")[1]
        if payload["data"]["status"] == "successful":
            try:
                update_invoice(payload)
                update_subscription(payload, school_id)
            except TransactionVerificationError as e:
                print(e.err["errMsg"])
                print(e.err["txRef"])
                return Response({"status": "error", "message": "Payment verification error"})
