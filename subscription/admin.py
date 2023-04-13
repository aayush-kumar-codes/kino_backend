from django.contrib import admin
from .models import Plan, Benefit, Subscription

# Register your models here.

admin.site.register(Plan)
admin.site.register(Benefit)
admin.site.register(Subscription)
