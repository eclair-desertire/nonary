import django
import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from shop.models import Property
from utils.utils import is_camel_case

for item in Property.objects.all():
    if item.name:
        if item.name.count(' ') == 0 and is_camel_case(item.name) and sum(map(str.isupper, item.name)) > 1:
            item.is_active = False
        else:
            item.is_active = True
        item.save()
