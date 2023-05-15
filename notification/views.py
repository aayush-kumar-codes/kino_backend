from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import NotificationSerializer
from rest_framework.permissions import IsAuthenticated
from .models import Notification

# Create your views here.


class NotificationAPI(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        notification = request.user.receiver.filter(
            is_read=False
        ).order_by('-created_at')
        params = self.request.query_params

        if params.get("view"):
            notification = request.user.receiver.all().order_by('-created_at')
        serializer = NotificationSerializer(notification, many=True)
        response = Response(serializer.data)
        response.success_message = "Your Notifications."
        return response

    def delete(self, request):
        notification = Notification.objects.filter(
            receiver=request.user.id, is_read=False
        )
        notification.update(is_read=True)
        response = Response(status=200)
        response.success_message = "Notifications cleared."
        return response
