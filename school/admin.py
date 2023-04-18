from django.contrib import admin
from .models import School, Term, Lesson, Class
# Register your models here.

admin.site.register(School)
admin.site.register(Term)
admin.site.register(Lesson)
admin.site.register(Class)
