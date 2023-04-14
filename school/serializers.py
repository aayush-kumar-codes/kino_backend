from rest_framework import serializers
from .models import School, Term, Lession
from utils.helper import generate_absolute_uri


class SchoolSerializer(serializers.ModelSerializer):
    subscriptions = serializers.SerializerMethodField()
    logo_img = serializers.SerializerMethodField()

    class Meta:
        model = School
        exclude = ("users", "cover")

    def get_subscriptions(self, instance):
        try:
            return instance.school_subscription.last().plan.name
        except Exception:
            return "KAINO SOCIAL"

    def get_logo_img(self, instance):
        request = self.context.get("request")
        return generate_absolute_uri(request, instance.logo_img.url)


class CreateSchoolSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = School
        exclude = ("users", "cover",)


class SchoolDataSerializer(serializers.ModelSerializer):
    subscriptions = serializers.SerializerMethodField()

    class Meta:
        model = School
        exclude = ("users", "cover")

    def get_subscriptions(self, instance):
        try:
            return instance.school_subscription.last().plan.name
        except Exception:
            return "KAINO SOCIAL"