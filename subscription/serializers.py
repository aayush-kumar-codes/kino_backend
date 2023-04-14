from rest_framework import serializers
from .models import Plan, Benefit, Subscription


class BenefitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Benefit
        fields = ("__all__")


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ("name", "price", "benefit")


class PlansSerializer(serializers.ModelSerializer):
    benefit = serializers.SerializerMethodField()
    currency = serializers.CharField(default="$")

    def get_benefit(self, instance):
        benefit = Benefit.objects.all()
        serializer = BenefitSerializer(benefit, many=True)
        return serializer.data

    class Meta:
        model = Plan
        fields = ("name", "price", "currency", "benefit")


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ("__all__")
