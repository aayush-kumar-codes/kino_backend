from django.urls import path
from .views import NotificationAPI

urlpatterns = [
    path('', NotificationAPI.as_view(), name='alert'),

]
