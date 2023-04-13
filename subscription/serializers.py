from rest_framework import serializers
from .models import Plan, Benefit, Subscription
from django.conf import settings


class BenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benefit
        fields = ("id","name",)


class PlanSerializer(serializers.ModelSerializer):
    benefit = serializers.SerializerMethodField()
    currency = serializers.CharField(default="$")

    def get_benefit(self, instance):
        return ""

    class Meta:
        model = Plan
        fields = ("name", "price","currency", "benefit")


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ("__all__")


class GetPlanSerializer(serializers.ModelSerializer):
    currency = serializers.CharField(default=settings.CURRENCY)

    class Meta:

        model = Plan
        fields = ("id","name", "price","currency", "benefits",)