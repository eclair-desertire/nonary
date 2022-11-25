import django
import os
import requests


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from external.services.products import get_product_images_and_properties_from_website


url = f'https://tvoy.kz/yml_get/v6gd7hf2k54t'

response = requests.get(url)

with open('feed.xml', 'wb') as file:
    file.write(response.content)

get_product_images_and_properties_from_website('feed.xml')
