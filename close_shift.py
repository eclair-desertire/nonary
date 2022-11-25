import django
import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from order.services.common import can_close_shift, auth_and_save_token
from django.conf import settings

headers = {
    'X-API-KEY': settings.WEBKASSA_API,
    'Content-Type': 'application/json'
}

token = auth_and_save_token()

can_close_shift(token, headers)
