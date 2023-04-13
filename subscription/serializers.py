from rest_framework import serializers
from .models import Plan, Benefit, Subscription


class BenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benefit
        fields = ("__all__")


class PlanSerializer(serializers.ModelSerializer):
    benefit = serializers.SerializerMethodField()
    currency = serializers.CharField(default="$")

    def get_benefit(self, instance):
        return str(BenefitSerializer.data)

    class Meta:
        model = Plan
        fields = ("name", "price", "benefit")


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ("__all__")
