from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager
from utils.helper import get_file_path

# Custom User model extending Django's AbstractUser
class User(AbstractUser):
    # Role constants
    Admin = 1
    Teacher = 2
    Student = 3
    Parent = 4

    # Role choices tuple for the role field
    ROLE_CHOICES = (
        (Admin, 'Admin'),
        (Student, 'Student'),
        (Teacher, 'Teacher'),
        (Parent, 'Parent'),
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
    mobile_no = models.CharField(max_length=10, blank=True)
    address = models.CharField(max_length=512, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    profile_img = models.ImageField(
        upload_to=get_file_path, height_field=None,
        width_field=None, max_length=100,
        blank=True, default=None
    )
    remember_me = models.BooleanField(default=False)

    # Required fields for Django's AbstractUser
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    # Custom User manager
    objects = UserManager()
