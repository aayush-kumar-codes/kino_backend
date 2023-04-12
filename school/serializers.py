from rest_framework import serializers
from .models import School
from users.models import User


class SchoolSerializer(serializers.ModelSerializer):
    students = serializers.SerializerMethodField()

    class Meta:
        model = School
        exclude = ("users", "cover",)

    def get_students(self, obj):
        return obj.users.filter(role=User.Student).count()


class CreateSchoolSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = School
        exclude = ("users", "cover",)
