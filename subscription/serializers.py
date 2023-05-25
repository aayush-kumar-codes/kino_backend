from rest_framework import serializers
from .models import Plan, Benefit, Subscription, Invoice, Item
from django.conf import settings
from users.models import User
from utils.helper import generate_absolute_uri
from django.db.models import Sum

class BenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benefit
        fields = ("id", "name",)


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ("name", "price", "benefit")


class SubscriptionSerializer(serializers.ModelSerializer):
    school = serializers.CharField(
        source="school.name", read_only=True
    )
    plan = serializers.CharField(source="plan.name", read_only=True)
    amount = serializers.CharField(source="plan.price", read_only=True)

    class Meta:
        model = Subscription
        fields = (
            "id", "school", "plan", "start_date", "is_paid",
            "amount"
        )


class GetPlanSerializer(serializers.ModelSerializer):
    currency = serializers.CharField(default=settings.CURRENCY)

    class Meta:
        model = Plan
        fields = ("id", "name", "price", "currency", "benefits",)


class InvoiceSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(
        source='organization.name', read_only=True
    )

    class Meta:
        model = Invoice
        fields = (
            "organization", "invoice_number", "invoice_from", "invoice_to",
            "po_number", "created_date", "due_date", "sign_img",
            "name_of_signee", "organization_name"
        )
        extra_kwargs = {"organization": {"write_only": True}}


class ItemSerializer(serializers.Serializer):
    invoice = serializers.JSONField(required=True)
    item = serializers.JSONField(required=True)


class InvoiceListSerializer(serializers.ModelSerializer):
    invoice_to = serializers.CharField(source='organization.name', read_only=True)
    logo = serializers.ImageField(source="organization.logo", read_only=True)
    category_name = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = (
            'id', 'invoice_to', "logo", 'category_name', 'created_date', 'due_date',
            'status', 'amount'
        )

    def get_status(self, status_instance):
        status = status_instance.get_status_display()
        return status

    def get_category_name(self, invoice_instance):
        if invoice_instance.invoice_amount.first():
            item = invoice_instance.invoice_amount.first().plan.name
            return item
        return ""

    def get_amount(self, invoice_instance):
        amount = invoice_instance.invoice_amount.aggregate(Sum('amount'))['amount__sum']
        return amount

    def get_logo(self, instance):
        request = self.context.get("request")
        if instance.logo:
            return generate_absolute_uri(request, instance.logo.url)
        return ""


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('address')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", 'mobile_no', 'address', 'zip_code']


class ItemsSerializer(serializers.ModelSerializer):
    plan = serializers.CharField(
        read_only=True, source="plan.name",
        default=None
    )
    item_name = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Item
        fields = ("id", "plan", "quantity", "price", "discount", "amount", "item_name")
    
    def get_item_name(self, instance):
        return instance.items

class ItemSerializers(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    sign_img = serializers.ImageField(read_only=True)
    organization_name = serializers.CharField(
        source='organization.name', read_only=True
    )
    status = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()


    class Meta:
        model = Invoice
        fields = ("organization", "invoice_number", "invoice_from", "invoice_to",
            "po_number", "created_date", "due_date", "status", "sign_img",
            "name_of_signee", "organization_name", "items", "total_amount")

    def get_items(self, instance):
        items = instance.invoice_amount.all()
        return ItemsSerializer(items, many=True).data

    def get_sign_img(self, instance):
        request = self.context.get("request")
        if instance.sign_img:
            return generate_absolute_uri(request, instance.sign_img.url)
        return ""

    def get_status(self, status_instance):
        status = status_instance.get_status_display()
        return status

    def get_total_amount(self, instance):
        total = instance.invoice_amount.aggregate(Sum('amount'))['amount__sum']
        return total


class SchoolSubscriptionSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source="school.name")
    plan_name = serializers.CharField(source="plan.name", read_only=True)
    price = serializers.CharField(source="plan.price", read_only=True)
    benefits = BenefitSerializer(many=True, read_only=True, source="plan.benefits")

    class Meta:
        model = Subscription
        fields = ("school_name", "plan_name", "price", "start_date", "end_date", "benefits",)


class SchoolPaymentHistorySerializer(serializers.ModelSerializer):
    invoice_id = serializers.SerializerMethodField()
    plan_name = serializers.CharField(source="plan.name", read_only=True)
    created_at = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ("id", "invoice_id", "plan_name", "created_at", "end_date", "amount", "balance", "status",)

    def get_invoice_id(self, instance):
        return instance.school.organization.organization_invoice.last().id

    def get_created_at(self, instance):
        return str(instance.created_at).split()[0]

    def get_status(self, status_instance):
        status = status_instance.get_is_paid_display()
        return status

    def get_amount(self, instance):
        return str(instance.school.organization.organization_invoice.last().invoice_amount.last().amount)

    def get_balance(self, instance):
        if instance.is_paid == Subscription.Paid:
            return 0
        if instance.is_paid == Subscription.Unpaid:
            return str(instance.school.organization.organization_invoice.last().invoice_amount.last().amount)
