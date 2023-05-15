from django.contrib import admin
from .models import School, Term, Lesson, Class, Organization
# Register your models here.

admin.site.register(Term)
admin.site.register(Lesson)
admin.site.register(Class)
admin.site.register(Organization)

@admin.register(School)
class SchoolDashboard(admin.ModelAdmin):
    list_display = ("id", "name", "organization",)
