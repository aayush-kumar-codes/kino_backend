from rest_framework import serializers
from .models import School, Term, Lesson, Class
from utils.helper import generate_absolute_uri
from django.conf import settings


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
            return "KAINO_SOCIAL"

    def get_logo_img(self, instance):
        request = self.context.get("request")
        if instance.logo_img:
            return generate_absolute_uri(request, instance.logo_img.url)
        return ""


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
            return settings.KINO_PLANS[0]


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = ('__all__')


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ("__all__")


class LessonSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source="_class.name", read_only=True)
    _class = serializers.CharField(required=False, write_only=True)

    class Meta:
        model = Lesson
        fields = ("__all__")
