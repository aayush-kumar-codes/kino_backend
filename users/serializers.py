from rest_framework import serializers
from .models import (
    User, ActivityLog, Parent, Teacher, Student, FLNImpact,
    RollCall, Address
)

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


class CreateMemberSerializer(serializers.Serializer):
    user = serializers.JSONField(required=True)
    member = serializers.JSONField(required=True)


class ParentSerializer(serializers.ModelSerializer):
    user = UserDataSerializer()
    assigned_students = serializers.SerializerMethodField(read_only=True)
    assigned_schools = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Parent
        fields = ("__all__")

    def get_assigned_students(self, instance):
        return instance.student_parent.count()

    def get_assigned_schools(self, instance):
        return instance.user.school_users.count()


class TeacherSerializer(serializers.ModelSerializer):
    user = UserDataSerializer()
    main_class = serializers.CharField(
        source="main_class.name", read_only=True
    )

    class Meta:
        model = Teacher
        fields = ("__all__")


class GetAllParentSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="user.id")
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    mobile_no = serializers.CharField(source="user.mobile_no")
    class Meta:
        model = Parent
        fields = ("id", "first_name", "last_name", "mobile_no")


class StudentSerializer(serializers.ModelSerializer):
    user = UserDataSerializer()
    parent = serializers.SerializerMethodField(read_only=True)
    _class = serializers.CharField(source="_class.name", read_only=True)

    class Meta:
        model = Student
        fields = ("__all__")

    def get_parent(self, instance):
        if instance.parent:
            return f"{instance.parent.user.first_name} {instance.parent.user.last_name}"
        return None


class FlnSerializer(serializers.ModelSerializer):
    class Meta:
        model = FLNImpact
        fields = ("accessment_area", "numbers")

class RollCallSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    _class = serializers.CharField(source="student._class")
    dob = serializers.CharField(source="student.user.dob")
    gender = serializers.CharField(source="student.user.gender")
    total_days_present = serializers.SerializerMethodField()
    total_days_absent = serializers.SerializerMethodField()
    profile_img = serializers.ImageField(source="student.user.profile_img")
    class Meta:
        model = RollCall
        fields = (
            "id", "attendance", "name", "_class", "dob", "gender",
            "total_days_present", "total_days_absent", "profile_img"
        )

    def get_name(self, instance):
        return f"{instance.student.user.first_name} {instance.student.user.last_name}"

    def get_total_days_present(self, instance):
        return instance.student.student_role_calls.filter(attendance=RollCall.Present).count()

    def get_total_days_absent(self, instance):
        return instance.student.student_role_calls.filter(attendance=RollCall.Absent).count()


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ("user", "street", "city", "district", "region", "zip_code", "country")


class AccountSerializer(serializers.ModelSerializer):
    address = AddressSerializer(source="user_address", many=True, read_only=True)

    class Meta:
        model = User
        fields = ("first_name", 'last_name', 'email', 'dob', 'mobile_no', "address")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['address'] = data['address'][0]
        return data


# class UserSerializer(serializers.ModelSerializer):
#     user_address = AddressSerializer(many=True)
#     class Meta:
#         model = User
#         fields = ('username', 'email', 'first_name', 'last_name', 'mobile_no','user_address')

#     def create(self, validated_data):
#         addresses_data = validated_data.pop('user_address')
#         user = User.objects.create(**validated_data)
#         for address_data in addresses_data:
#             Address.objects.create(user=user, **address_data)
#         return user
