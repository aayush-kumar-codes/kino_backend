from .models import OTP
from django.conf import settings
from twilio.rest import Client
from django.core.mail import send_mail
from rest_framework.response import Response


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
        recipient_list = [username, ]
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        data = {
            "is_two_factor": 1
        }
        response = Response(data, status=200)
        response.success_message = "Otp send successfully."
        return response
