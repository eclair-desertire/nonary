import django
import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from external.services.commerce_ml_import import get_or_create_import_status, fetch_storehouse_from_xml, \
    fetch_categories_from_xml, fetch_goods_from_xml, fetch_prices_from_xml, fetch_rests_from_xml

try:
    fetch_storehouse_from_xml('sklady.xml', filename='sklady.xml')
except FileNotFoundError:
    print('NoFile')
try:
    fetch_categories_from_xml('soglasheniya.xml', filename='soglasheniya.xml')
except FileNotFoundError:
    print('NoFile')
try:
    fetch_goods_from_xml('goods.xml', filename='goods.xml')
except FileNotFoundError:
    print('NoFile')
try:
    fetch_prices_from_xml('pay_with_carduid.xml', filename='pay_with_carduid.xml')
except FileNotFoundError:
    print('NoFile')
try:
    fetch_rests_from_xml('rests.xml', filename='rests.xml')
except FileNotFoundError:
    print('NoFile')
