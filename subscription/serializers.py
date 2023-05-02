from rest_framework import serializers
from .models import Plan, Benefit, Subscription, Invoice
from django.conf import settings


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
    class Meta:
        model = Invoice
        fields = ("__all__")
