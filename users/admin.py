from django.contrib import admin

from .models import User, CustomPermission, ActivityLog, OTP
# Register your models here.

admin.site.register(User)
admin.site.register(CustomPermission)
admin.site.register(ActivityLog)
admin.site.register(OTP)
