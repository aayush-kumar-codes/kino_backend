from rest_framework import serializers
from .models import User, ActivityLog, Parent, Teacher, Student, FLNImpact


# UserSerializer: Serializer for User model
class UserSerializer(serializers.ModelSerializer):
    # Meta class to define model and fields to be serialized
    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'role')

    # Override create method to create a new User instance
    def create(self, validated_data):
        # Create a new user using validated_data
        user = User.objects.create_user(**validated_data)

        # Return the created user instance
        return user


# PasswordSerializer: Serializer for password change
class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField()  # Field for the new password
    confirm_password = serializers.CharField()  # Field for the confirmation of the new password
    token = serializers.CharField()
    uid = serializers.CharField()


class AccessRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class RoleSerializer(serializers.ModelSerializer):
    last_active = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id", "first_name", "last_name", "profile_img",
            "email", "role", "last_active", "permission"
        )

    def get_last_active(self, instance):
        return str(instance.last_login).split()[0]


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityLog
        fields = ("__all__")


class UpdateConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("is_activity_log", "is_two_factor",)


class TwoFALoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    otp = serializers.IntegerField()


class UpdatePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()
    re_password = serializers.CharField()


class UserDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id", "username", "email", "first_name",
            "last_name", "gender", "dob", "mobile_no", "profile_img",
        )


class ParentSerializer(serializers.ModelSerializer):
    user = UserDataSerializer()

    class Meta:
        model = Parent
        fields = ("__all__")

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data, role=User.Parent)
        parent = Parent.objects.create(user=user, **validated_data)
        return parent


class TeacherSerializer(serializers.ModelSerializer):
    user = UserDataSerializer()
    main_class = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = ("__all__")

    def get_main_class(self, instance):
        return instance.main_class.name

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data, role=User.Teacher)
        teacher = Teacher.objects.create(user=user, **validated_data)
        return teacher


class StudentSerializer(serializers.ModelSerializer):
    user = UserDataSerializer()
    parent = serializers.SerializerMethodField(read_only=True)
    _class = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Student
        fields = ("__all__")

    def get_parent(self, instance):
        return f"{instance.parent.user.first_name} {instance.parent.user.last_name}"

    def get__class(self, instance):
        return instance._class.name

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data, role=User.Student)
        student = Student.objects.create(user=user, **validated_data)
        return student


class FlnSerializer(serializers.ModelSerializer):
    class Meta:
        model = FLNImpact
        fields = ("accessment_area", "numbers")
