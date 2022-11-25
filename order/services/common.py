import json
from decimal import Decimal

import after_response
import requests
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import OuterRef, Subquery, F, Case, When, Sum, IntegerField
from django.db.models.functions import Cast
from django.utils.translation import gettext_lazy as _

from rest_framework.fields import DecimalField

from utils.choices import DiscountTypeChoices, StorehouseTypeChoices
from utils.custom_logging import save_warning, save_info

User = get_user_model()

OrderItem = apps.get_model(app_label='order', model_name="OrderItem")
Rest = apps.get_model(app_label='shop', model_name="Rest")
ProductPrice = apps.get_model(app_label='shop', model_name='ProductPrice')
UserCard = apps.get_model(app_label='auth_user', model_name='UserCard')
City = apps.get_model(app_label='location', model_name='City')
WebkassaToken = apps.get_model(app_label='order', model_name='WebkassaToken')


def recalculate_to_pay_price(order, to_pay):
    if order.promo:
        if order.promo.discount_type == DiscountTypeChoices.FIXED:
            to_pay -= order.promo.value
        else:
            to_pay = to_pay - (to_pay * order.promo.value / 100)
    # if order.delivery:
    #     to_pay += order.delivery.price
    return to_pay


def _get_all_order_items(order, city_slug=None):
    if hasattr(order, 'address') and order.address:
        city_slug = order.address.address.city.slug
    elif hasattr(order, 'pickup') and order.pickup:
        city_slug = order.pickup.pickup.city.slug
    elif hasattr(order, 'post') and order.post:
        city_slug = order.post.post.city.slug
    else:
        if city_slug is None:
            city = City.objects.filter(is_active=True, storehouses__isnull=False)
            if city.exists():
                city_slug = city.first().slug
    # discount_price_subquery = ProductPrice.objects.filter(
    #     product_id=OuterRef('product_id'),
    #     storehouse__storehouse_type=StorehouseTypeChoices.DISCOUNT,
    #     storehouse__cities__slug=city_slug,
    # ).values('price')[:1]
    # product_rest_subquery = Rest.objects.filter(
    #     product_id=OuterRef('product_id'),
    #     storehouse__storehouse_type=StorehouseTypeChoices.DISCOUNT,
    #     storehouse__cities__slug=city_slug,
    # ).values('quantity')[:1]
    # price_subquery = ProductPrice.objects.filter(
    #     product_id=OuterRef('product_id'),
    #     storehouse__storehouse_type=StorehouseTypeChoices.BASIC,
    #     storehouse__cities__slug=city_slug,
    # ).values('price')[:1]
    qs = OrderItem.objects.filter(order=order).select_related(
        'product'
    ).alias(
        # price_alias=F(f'prices_dict__{city_slug}_{StorehouseTypeChoices.BASIC}'),
        # discount_price_alias=F(f'prices_dict__{city_slug}_{StorehouseTypeChoices.DISCOUNT}'),
        # price_alias=Subquery(price_subquery),
        # discount_price_alias=Subquery(discount_price_subquery),
    ).annotate(
        # rest=Subquery(product_rest_subquery),
        original_price=Cast(
            F(f'product__prices_dict__{city_slug}_{StorehouseTypeChoices.BASIC}'),
            IntegerField()
        ) * F('quantity'),
        price=Cast(
            F(f'product__prices_dict__{city_slug}_{StorehouseTypeChoices.DISCOUNT}'),
            IntegerField()
        ) * F('quantity')
    )
    for item in qs:
        item.product_price = item.price
        item.product_original_price = item.original_price
        item.save()
    # qs.update(
    #     product_price=F('original_price'),
    #     product_original_price=F('price')
    # )
    return qs


def recalculate_total_price(order):
    order_items = _get_all_order_items(order)
    total_price = sum(item.price for item in order_items)
    original_price = sum(item.original_price for item in order_items)
    return total_price, original_price


def get_order_delivery_address(instance):
    text = ''
    if hasattr(instance, 'address') and instance.address:
        text = f"г. {instance.address.address.city.name}, {instance.address.address.street}"
        if instance.address.address.office:
            text += f", {instance.address.address.office}"
    elif hasattr(instance, 'pickup') and instance.pickup:
        text = f"г. {instance.pickup.pickup.city.name}, {instance.pickup.pickup.address}"
    elif hasattr(instance, 'post') and instance.post:
        text = f"г. {instance.post.post.city.name}, {instance.post.post.address}"
    return text


def get_order_user_data(key, order):
    if order.user:
        result = getattr(order.user, key)
        if result:
            return result
    return _('Не заполнено')


def auth_webkassa(headers):
    url = f"https://{settings.WEBKASSA_URL}/api/Authorize"
    request_body = {
        'Login': settings.WEBKASSA_USERNAME,
        'Password': settings.WEBKASSA_PASSWORD,
    }
    resp = requests.post(url, json.dumps(request_body), headers=headers)
    if resp.status_code < 300:
        try:
            response = resp.json()
        except Exception as _:
            response = json.loads(resp.text)
        if 'Data' in response:

            return response.get('Data', {}).get('Token')
        for err in response.get('Errors', []):
            save_warning(f"Error on WebKassa Auth, text: {err.get('Text')}, Code: {err.get('Code')}")
    save_warning(f"Error on WebKassa Auth, status: {resp.status_code}")
    return None


def get_order_modifiers(order):
    modifiers = []
    if order.delivery and order.delivery.price > Decimal(0.0):
        modifiers.append({
            'Sum': float(order.delivery.price),
            'Text': 'Доставка',
            'Tax': round(float(order.delivery.price) - float(order.delivery.price) * 100 / 112, 2),
            'TaxType': 100,
            'Type': 2,
            'TaxPercent': 12
        })
    if order.promo:
        if order.promo.discount_type == DiscountTypeChoices.FIXED:
            promo_sum = float(order.promo.value)
        else:
            promo_sum = round(float(order.total_price * order.promo.value) / 100)
        modifiers.append({
            'Sum': promo_sum,
            'Text': order.promo.name,
            'Tax': round(promo_sum - promo_sum * 100 / 112, 2),
            'TaxType': 100,
            'Type': 1,
            'TaxPercent': 12
        })
    return modifiers


def get_order_positions(order):
    order_items = OrderItem.objects.filter(order=order)
    positions = []
    iter_ind = 1
    for idx, item in enumerate(order_items):
        product_price = float(item.product_price) / item.quantity
        positions.append({
            'Count': item.quantity,
            'Price': product_price,
            'TaxPercent': 12,
            'Tax': round(product_price - product_price / 1.12, 2),
            'TaxType': 100,
            'PositionName': item.product.name,
            'PositionCode': f'{idx+iter_ind}',
            'Discount': 0,
            'Markup': 0,
            'SectionCode': "1",
            'UnitCode': item.product.base_unit,
            'GTIN': item.product.barcode,
            'ProductId': item.product_id,
            'WarehouseType': 1
        })
    return positions


def can_close_shift(token, headers):
    url = f"https://{settings.WEBKASSA_URL}/api/ZReport"
    resp = requests.post(url, json={
        'Token': token,
        'CashboxUniqueNumber': settings.WEBKASSA_ID
    }, headers=headers)
    if resp.status_code < 300:
        try:
            response = resp.json()
        except Exception as _:
            response = json.loads(resp.text)
        if 'Data' in response:
            return 'shift'
        else:
            save_warning(f"Status: {resp.status_code}. Message: {json.dumps(response)}")
    else:
        save_warning(f"Status: {resp.status_code}. Message: {resp.text}")
    return 'no_error'


def auth_and_save_token():
    headers = {
        'X-API-KEY': settings.WEBKASSA_API,
        'Content-Type': 'application/json'
    }
    token = auth_webkassa(headers)
    WebkassaToken.objects.create(token=token)
    return token


def check_error_webkassa(response, token, headers):
    errors = response.get('Errors', [])
    close_shift_error = list(filter(lambda x: x.get('Code') == 11, errors))
    unauth_error = list(filter(lambda x: x.get('Code') in [3, 2, 1], errors))
    if len(unauth_error) > 0:
        return 'auth'
    if len(close_shift_error) > 0:
        return can_close_shift(token, headers)
    return 'other'


def send_check_data_webkassa(order, token, headers):
    url = f"https://{settings.WEBKASSA_URL}/api/Check"
    positions = get_order_positions(order)
    modifiers = get_order_modifiers(order)
    data = {
        'Token': token,
        'CashboxUniqueNumber': settings.WEBKASSA_ID,
        'OperationType': 2,
        'Positions': positions,
        'Payments': [{
            'Sum': round(float(order.to_pay_price)),
            'PaymentType': 1
        }],
        'TicketModifiers': modifiers,
        'Change': 0,
        'RoundType': 2,
        'ExternalCheckNumber': order.order_id,
        'CustomerEmail': order.user.email,
        'CustomerPhone': order.user.phone_number,
    }
    save_info(f'WEBKASSA - {data}')
    resp = requests.post(url, json.dumps(data), headers=headers)
    if resp.status_code < 300:
        try:
            response = resp.json()
        except Exception as _:
            response = json.loads(resp.text)
        if 'Data' in response:
            order.ticket_url = response.get('Data').get('TicketUrl')
            order.ticket_print_url = response.get('Data').get('TicketPrintUrl')
            order.save()
        else:
            save_warning(f"Status: {resp.status_code}. Message: {json.dumps(response)}")
            error = check_error_webkassa(response, token, headers)
            if error in ['auth', 'shift']:
                if error == 'auth':
                    token = auth_and_save_token()
                send_check_data_webkassa(order, token, headers)
                return
    else:
        save_warning(f"Status: {resp.status_code}. Message: {resp.text}")
        try:
            response = resp.json()
        except Exception as _:
            response = json.loads(resp.text)
        if 'Errors' in response:
            error = check_error_webkassa(response, token, headers)
            if error in ['auth', 'shift']:
                if error == 'auth':
                    token = auth_and_save_token()
                send_check_data_webkassa(order, token, headers)
                return


@after_response.enable
def send_webkassa(order):
    headers = {
        'X-API-KEY': settings.WEBKASSA_API,
        'Content-Type': 'application/json'
    }
    webkassa = WebkassaToken.objects.last()
    if webkassa:
        token = webkassa.token
        if token:
            send_check_data_webkassa(order, token, headers)
        else:
            token = auth_and_save_token()
            send_check_data_webkassa(order, token, headers)
    else:
        token = auth_and_save_token()
        send_check_data_webkassa(order, token, headers)
