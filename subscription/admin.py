from django.contrib import admin
from .models import Plan, Benefit, Subscription, Invoice, Item

# Register your models here.

admin.site.register(Plan)
admin.site.register(Benefit)
admin.site.register(Subscription)
admin.site.register(Invoice)
# admin.site.register(Item)
@admin.register(Item)
class SchoolDashboard(admin.ModelAdmin):
    list_display = ("invoice", "plan", "amount",)