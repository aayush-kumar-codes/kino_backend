from django.db import models
from utils.helper import get_file_path
from users.models import User
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.


class Term(models.Model):
    term_start_date = models.DateField()
    mid_term_break = models.DateField()
    term_end_date = models.DateField()
    term_name = models.CharField(max_length=255)
    country = models.CharField(max_length=150)
    academic_term = models.CharField(max_length=124)
    academic_year = models.CharField(max_length=4, default=1900)
    weeks = models.IntegerField()
    months = models.IntegerField()
    exam_start_date = models.DateField(null=True, blank=True)
    exam_end_date = models.DateField(null=True, blank=True)
    other_events = models.CharField(max_length=124, null=True, blank=True)
    event_start_date = models.DateField(null=True, blank=True)
    event_end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.term_name


class School(models.Model):
    users = models.ManyToManyField(User)
    name = models.CharField(max_length=255, unique=True)
    year_established = models.DateField()
    motto = models.CharField(max_length=255)
    term_system = models.ForeignKey(
        Term, on_delete=models.CASCADE, related_name="term"
    )
    total_students = models.IntegerField()
    total_teachers = models.IntegerField(null=True, blank=True)
    principal_name = models.CharField(max_length=124)
    phone = PhoneNumberField(unique=True)
    website_url = models.URLField(max_length=255)
    email = models.EmailField(unique=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    region = models.CharField(max_length=255)
    city = models.CharField(max_length=124)
    country = models.CharField(max_length=124)
    description = models.CharField(max_length=512)
    cover = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    logo_img = models.ImageField(
        upload_to=get_file_path, null=True, blank=True
    )

    def __str__(self):
        return self.name


class Class(models.Model):
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name


class Lesson(models.Model):
    name = models.CharField(max_length=124)
    subject_id = models.CharField(max_length=124)
    _class = models.ForeignKey(
        Class, on_delete=models.CASCADE, null=True,
        blank=True, related_name="lesson_class"
    )
    learning_area = models.CharField(max_length=100)
    term = models.ForeignKey(
        Term, on_delete=models.CASCADE, related_name="lesson_term"
    )
    week = models.IntegerField()
    country = models.CharField(max_length=124)

    def __str__(self):
        return self.name
