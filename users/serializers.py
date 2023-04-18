from rest_framework import serializers
from .models import User


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
    id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id", "first_name", "last_name", "profile_img",
            "email", "role", "last_active", "permission"
        )

    def get_last_active(self, instance):
        return str(instance.last_login).split()[0]

    def get_id(self, instance):
        return instance.id
