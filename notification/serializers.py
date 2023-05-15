from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Notification
        fields = ("id", "sender", "message", "created_at", "is_read")

    def get_sender(self, instance):
        return f"{instance.sender.first_name} {instance.sender.last_name}"
