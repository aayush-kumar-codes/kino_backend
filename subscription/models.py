from django.db import models
from school.models import School, Organization
from utils.helper import get_file_path

# Create your models here.


class Benefit(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name


class Plan(models.Model):
    KAINO_PLUS = "KAINO_PLUS"
    KAINO_BASIC = "KAINO_BASIC"
    KAINO_SOCIAL = "KAINO_SOCIAL"

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
    Paid = 1
    Unpaid = 2
    Due = 3
    Overdue = 4
    Cancelled = 5
    Recurring = 6
    Draft = 7

    STATUS_CHOICE = (
        (Paid, 'Paid'),
        (Unpaid, 'Unpaid'),
        (Due, 'Due'),
        (Overdue, 'OverDue'),
        (Cancelled, 'Cancelled'),
        (Recurring, 'Recurring'),
        (Draft, 'Draft'),
    )
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE,
        related_name='organization_invoice'
    )
    invoice_number = models.CharField(
        max_length=20, unique=True
    )
    status = models.PositiveSmallIntegerField(
        choices=STATUS_CHOICE, default=Unpaid
    )
    invoice_from = models.CharField(max_length=500)
    invoice_to = models.CharField(max_length=500)
    po_number = models.CharField(max_length=15)
    created_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    sign_img = models.ImageField(
        upload_to=get_file_path, null=True, blank=True
    )
    name_of_signee = models.CharField(max_length=124, null=True, blank=True)

    file_dir = "invoice/signature"

    def __str__(self):
        return self.organization.name



class Item(models.Model):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name='invoice_amount'
    )
    items = models.CharField(max_length=500)
    plan = models.ForeignKey(
        Plan, on_delete=models.CASCADE, related_name='item_plan'
    )
    quantity = models.IntegerField()
    price = models.IntegerField()
    discount = models.IntegerField()
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    def save(self, *args, **kwargs):
        self.amount = self.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return self.invoice.invoice_number
