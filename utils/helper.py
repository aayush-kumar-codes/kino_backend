import uuid
import os, requests
from django.conf import settings


def get_file_path(instance, filename):
    file_dir = instance.file_dir
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join(file_dir, filename)


def generate_absolute_uri(request, url):
    return request.build_absolute_uri(url)


def get_view_permissions(request, view):
    required_permissions = view.get_required_permissions().value
    permissions = request.user.permission.all().values_list(
        "code_id", flat=True
    )
    return required_permissions, permissions


def get_calculated_amount(instance, quantity, discount):

    try:
        amount = (instance.price * quantity) * discount / 100
    except:
        amount = instance.price * quantity
    return amount


def get_ip():
    try:
        response = requests.get(settings.IPIFY_API_URL)
        return response.json()['ip']
    except Exception as e:
        return ""