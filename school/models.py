from django.db import models
from utils.helper import get_file_path
from users.models import User
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth import get_user_model

# Create your models here.


class Organization(models.Model):
    name = models.CharField(max_length=124)
    email = models.EmailField(unique=True)
    logo = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    address = models.CharField(
        max_length=225, null=True, blank=True, default=None
    )
    city = models.CharField(
        max_length=124, null=True, blank=True, default=None
    )
    country = models.CharField(max_length=124)

    file_dir = "organozation/logo"

    def __str__(self):
        return self.name


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
    users = models.ManyToManyField(User, related_name="school_users")
    organization = models.ForeignKey(
        Organization, on_delete=models.SET_NULL, related_name="organization",
        null=True, blank=True
    )
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

    file_dir = "school/logo"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        User = get_user_model()
        password = User.objects.make_random_password()
        user, created  = User.objects.get_or_create(email=self.email, first_name="School", last_name="Admin", role=User.School_Admin)
        if created:
            user.set_password(password)
            user.save()
        super().save(*args, **kwargs)
        self.users.add(user)


class Class(models.Model):
    name = models.CharField(max_length=50)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name


class Lesson(models.Model):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, null=True,
        blank=True, related_name="school_lesson"
    )
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
    is_covered = models.BooleanField(default=False)

    def __str__(self):
        return self.name
