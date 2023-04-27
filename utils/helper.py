import uuid
import os
import requests
from django.conf import settings

def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('uploads/logos', filename)


def generate_absolute_uri(request, url):
    return request.build_absolute_uri(url)


def get_view_permissions(request, view):
    required_permissions = view.get_required_permissions().value
    permissions = request.user.permission.all().values_list(
        "code_id", flat=True
    )
    return required_permissions, permissions


def get_ip():
    try:
        response = requests.get(settings.IPIFY_API_URL)
        return response.json()['ip']
    except Exception:
        return ""
    