from .models import OTP
from django.conf import settings
from twilio.rest import Client
from django.core.mail import send_mail
from rest_framework.response import Response
from datetime import datetime, timedelta, time, date
from django.db.models import Q
import calendar


def OTPgenerate(username, obj):
    print(type(username))
    if username == obj.mobile_no:
        instance, _ = OTP.objects.update_or_create(
            phone_number=username
        )
        instance.save()

        client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
        message = client.messages.create(
            from_=settings.MESSAGING_SERVICE_SID,
            to=username,
            body="Your OTP is: {}".format(instance.otp)
        )
        return Response("send")
    else:
        instance, _ = OTP.objects.update_or_create(
            email=username
        )
        instance.save()
        subject = "Account Verification"
        message = "Your OTP is: {}".format(instance.otp)
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [username,]
        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        except Exception as e:
            print("Email Exception", str(e))
        data = {
            "is_two_factor": 1
        }
        response = Response(data, status=200)
        response.success_message = "Otp send successfully."
        return response


def graph_data(params):
    key = {}
    if params.get("weekly"):
        start_date = datetime.today() - timedelta(days=7)

        for i in range(7):
            day = start_date + timedelta(days=i)
            key[day.strftime("%a")] = Q(date=day)

        lists = list(key.keys())
        return lists, key

    if params.get("day"):
        dates = date.today()
        for i in range(0, 24, 4):
            start_time = datetime.combine(dates, time(i, 0, 0))
            end_time = datetime.combine(dates, time(i, 59, 59))
            key[i] = Q(date__range=[start_time, end_time])

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
            date__range=[start_date, end_date]
        )
    lists = list(key.keys())
    return lists, key
