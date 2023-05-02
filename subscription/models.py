from django.db import models
from school.models import School
import uuid

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
    Paid = 1
    Unpaid = 2
    Due = 3
    Overdue = 4

    STATUS_CHOICE = (
        (Paid, 'Paid'),
        (Unpaid, 'Unpaid'),
        (Due, 'Due'),
        (Overdue, 'OverDue')
    )

    school = models.ForeignKey(
        School, on_delete=models.CASCADE,
        related_name="school_subscription"
    )
    plan = models.ForeignKey(
        Plan, on_delete=models.CASCADE, related_name="subscription_plan"
    )
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    is_paid = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICE, default=2
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(
        auto_now_add=False, null=True, blank=True
    )

    def __str__(self):
        return f"{self.school.name}'s {self.plan.name} Subscription"


class Invoice(models.Model):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name="school_invoice"
    )
    subscription = models.CharField(max_length=200)
    invoice_number = models.CharField(max_length=20,
        default='IN{}'.format(str(uuid.uuid4().int & (10**12-1)).zfill(12)),
        editable=False)
    invoice_from = models.CharField(max_length=500)
    invoice_to = models.CharField(max_length=500)
    po_number = models.IntegerField()
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()

    def __str__(self):
        return self.school.name


class Item(models.Model):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name='invoice_amount'
    )
    items = models.OneToOneField(
        Plan, on_delete=models.CASCADE, related_name="plan"
    )
    category_name = models.CharField(max_length=500)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.IntegerField()

    def save(self, *args, **kwargs):
        self.amount = self.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return self.category_name
