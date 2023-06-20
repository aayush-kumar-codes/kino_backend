from datetime import datetime, timedelta, date, time
from django.db.models import Q
import calendar, uuid
from .models import Invoice, Subscription, School, Plan
from rave_python import Rave
from dotenv import load_dotenv
import os
load_dotenv()


def graph_data(params):
    key = {}
    if params.get("weekly"):
        start_date = datetime.today() - timedelta(days=7)

        for i in range(7):
            day = start_date + timedelta(days=i)
            key[day.strftime("%a")] = Q(created_at__date=day)

        lists = list(key.keys())
        return lists, key
    if params.get("day"):
        dates = date.today()
        for i in range(0, 24, 4):
            start_time = datetime.combine(dates, time(i, 0, 0))
            end_time = datetime.combine(dates, time(i, 59, 59))
            key[i] = Q(created_at__range=[start_time, end_time])

        lists = list(key.keys())
        return lists, key

    current_year = datetime.today().year
    for i in range(1, 13):
        month_name = calendar.month_name[i][:3]
        start_date = datetime(current_year, i, 1)
        end_date = datetime(
            current_year, i, calendar.monthrange(current_year, i)[1]
        )
        key[month_name] = Q(
            created_at__range=[start_date, end_date]
        )
    lists = list(key.keys())
    return lists, key


def generate_invoice_number():
    invoice_number = 'IN{}'.format(str(uuid.uuid4().int)[:12])
    return invoice_number


def update_invoice(payload):
    invoice_no = payload["data"]["tx_ref"].split("/")[0]
    invoice = Invoice.objects.get(invoice_number=invoice_no)
    if payload["data"]["status"] == "successful":
        invoice.status = Invoice.Paid
        invoice.save()
    else:
        invoice.status = Invoice.Unpaid
        invoice.save()


def update_subscription(payload, school_id):
    PublicKey = os.getenv("PUBLIC_KEY")
    SecretKey = os.getenv("RAVE_SECRET_KEY")
    rave = Rave(PublicKey, SecretKey, production=False, usingEnv=True)
    subscriptions = rave.Subscriptions.all()
    plans = rave.PaymentPlan.fetch(subscriptions["returnedData"]["data"]["plansubscriptions"][0]["plan"])
    plaan = Plan.objects.get(name=plans["returnedData"]["data"]["paymentplans"][0]["name"])
    Subscription.objects.update_or_create(
        school=school_id,
        defaults={
            "plan": plaan,
            "end_date": subscriptions["returnedData"]["data"]["plansubscriptions"][0]["next_due"].split("T")[0],
            "is_paid": Subscription.Paid,
            "updated_at": payload["data"]["created_at"],
            "is_active": True
        }
    )
