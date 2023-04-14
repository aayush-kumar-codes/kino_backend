from django.db import models
from school.models import School

# Create your models here.


class Benefit(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name


class Plan(models.Model):
    name = models.CharField(max_length=124)
    price = models.IntegerField()
    benefits = models.ManyToManyField(Benefit)

    def __str__(self):
        return self.name


class Subscription(models.Model):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE,
        related_name="school_subscription"
    )
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(
        auto_now_add=False, null=True, blank=True
    )

    def __str__(self):
        return f"{self.school.name}'s {self.plan.name} Subscription"
