from rest_framework import serializers
from .models import School
from users.models import User


class SchoolSerializer(serializers.ModelSerializer):
    students = serializers.SerializerMethodField()
    subscriptions = serializers.SerializerMethodField()

    class Meta:
        model = School
        exclude = ("users", "cover")

    def get_students(self, instance):
        return instance.users.filter(role=User.Student).count()

    def get_subscriptions(self, instance):
        try:
            return instance.school_subscription.last().plan.name
        except Exception:
            return "KAINO SOCIAL"


class CreateSchoolSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = School
        exclude = ("users", "cover",)
