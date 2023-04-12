from django.db import models
from utils.helper import get_file_path
from users.models import User
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.


class School(models.Model):
    users = models.ManyToManyField(User)
    name = models.CharField(max_length=255, unique=True)
    year_established = models.DateField()
    motto = models.CharField(max_length=255)
    term_system = models.CharField(max_length=124)
    total_students = models.IntegerField()
    total_teachers = models.IntegerField(null=True, blank=True)
    principal_name = models.CharField(max_length=124)
    phone = PhoneNumberField()
    website_url = models.URLField(max_length=255)
    email = models.EmailField(unique=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    region = models.CharField(max_length=255)
    city = models.CharField(max_length=124)
    country = models.CharField(max_length=124)
    description = models.CharField(max_length=512)
    cover = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    logo_img = models.ImageField(upload_to=get_file_path, null=True, blank=True)

    def __str__(self):
        return self.name


class Term(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    term_start_date = models.DateField()
    mid_term_break = models.DateField()
    term_end_date = models.DateField()
    term_name = models.CharField(max_length=255)
    country = models.CharField(max_length=150)
    academic_term = models.CharField(max_length=124)
    academic_year = models.DateField()
    weeks = models.IntegerField()
    months = models.IntegerField()
    exam_start_date = models.DateField(null=True, blank=True)
    exam_end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.term_name


class Lession(models.Model):
    name = models.CharField(max_length=124)
    _class = models.CharField(max_length=50)
    learning_area = models.CharField(max_length=100)
    term = models.ForeignKey(Term, on_delete=models.CASCADE, null=True, blank=True)
    week = models.CharField(max_length=10)
    country = models.CharField(max_length=124)

    def __str__(self):
        return self.name
