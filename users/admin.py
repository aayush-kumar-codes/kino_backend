from django.contrib import admin

from .models import User, CustomPermission
# Register your models here.

admin.site.register(User)
admin.site.register(CustomPermission)
