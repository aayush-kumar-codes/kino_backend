from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager
from utils.helper import get_file_path, get_ip
from phonenumber_field.modelfields import PhoneNumberField
import random
from datetime import timedelta, datetime
from user_agents import parse
from django.utils import timezone


class CustomPermission(models.Model):
    code_name = models.CharField(max_length=100)
    code_id = models.IntegerField()

    def __str__(self):
        return f"{self.code_name} {self.code_id}"


# Custom User model extending Django's AbstractUser
class User(AbstractUser):
    # Role constants
    Admin = 1
    Teacher = 2
    Student = 3
    Parent = 4
    Head_of_curicullum = 5
    Content_creator = 6
    Finance = 7

    # Role choices tuple for the role field
    ROLE_CHOICES = (
        (Admin, 'Admin'),
        (Student, 'Student'),
        (Teacher, 'Teacher'),
        (Parent, 'Parent'),
        (Head_of_curicullum, 'Head_of_curicullum'),
        (Content_creator, 'Content_creator'),
        (Finance, 'Finance'),
    )

    # Gender constants
    Male = 1
    Female = 2

    # Gender choices tuple for the gender field
    GENDER = (
        (Male, 'Male'),
        (Female, 'Female'),
    )

    # User model fields
    email = models.EmailField(('email_address'), unique=True, max_length=200)
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=3)
    gender = models.PositiveSmallIntegerField(
        choices=GENDER, blank=True, null=True
    )
    dob = models.DateField(null=True, blank=True)
    mobile_no = PhoneNumberField(unique=True, null=True, blank=True)
    address = models.CharField(max_length=512, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)

    profile_img = models.ImageField(
        upload_to=get_file_path, height_field=None,
        width_field=None, max_length=100,
        blank=True, default=None
    )
    remember_me = models.BooleanField(default=False)
    permission = models.ManyToManyField(
        CustomPermission, related_name="user_permission"
    )
    is_activity_log = models.BooleanField(default=False)
    is_two_factor = models.BooleanField(default=False)

    file_dir = "user/profile"

    # Required fields for Django's AbstractUser
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    # Custom User manager
    objects = UserManager()

    def save(self, *args, **kwargs):
        self.username = self.email
        super().save(*args, **kwargs)


class ActivityLog(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_activity"
    )
    browser = models.CharField(max_length=124)
    ip_address = models.CharField(max_length=16)
    date = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=255)
    is_activity = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.action}"
    
    @staticmethod
    def create_activity_log(request, message):
        try:
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            if request.user:
                browser_name = parse(user_agent).browser.family
                activity_log = ActivityLog(
                    user=request.user,
                    browser=browser_name,
                    ip_address=get_ip(),
                    action=message,
                    is_activity=True,
                    date=timezone.now()
                )
                activity_log.save()
        except Exception as e:
            print("Exception", str(e))


class OTP(models.Model):
    email = models.EmailField(
        ('email_address'), unique=True, max_length=200, null=True, blank=True
    )
    phone_number = PhoneNumberField(unique=True, blank=True, null=True)
    otp = models.IntegerField()
    expire_time = models.DateTimeField()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        self.otp = random.randint(100000, 999999)
        self.expire_time = datetime.now() + timedelta(minutes=5)
        super().save(*args, **kwargs)


class Parent(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="parent", primary_key=True
    )
    occupation = models.CharField(max_length=124)
    assigned_students = models.IntegerField()
    nin = models.CharField(unique=True, max_length=255)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=124)
    region = models.CharField(max_length=124)
    country = models.CharField(max_length=124)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Teacher(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="teacher",
        primary_key=True
    )
    teacher_id = models.CharField(unique=True, max_length=124)
    joining_date = models.DateField()
    year_of_experience = models.IntegerField()
    qualification = models.CharField(max_length=255)
    main_class = models.ForeignKey(
        "school.Class", on_delete=models.CASCADE, related_name="class_teacher"
    )
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=124)
    region = models.CharField(max_length=124)
    country = models.CharField(max_length=124)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Student(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="student",
        primary_key=True
    )
    parent = models.ForeignKey(
        Parent, on_delete=models.CASCADE, related_name="student_parent",
        null=True, blank=True
    )
    id_no = models.CharField(unique=True, max_length=124)
    _class = models.ForeignKey(
        "school.Class", on_delete=models.CASCADE, related_name="class_student"
    )
    # school_type = models.CharField(max_length=50)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=124)
    region = models.CharField(max_length=124)
    country = models.CharField(max_length=124)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
