from django.contrib import admin

from .models import (
    User, CustomPermission, ActivityLog, OTP, Parent, Teacher,
    Student
)
# Register your models here.

admin.site.register(User)
admin.site.register(CustomPermission)
admin.site.register(OTP)
admin.site.register(Parent)
admin.site.register(Teacher)
admin.site.register(Student)

@admin.register(ActivityLog)
class ActivityDashBoard(admin.ModelAdmin):
    list_display = ("id", "ip_address", "browser", "action")
    