import requests
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader
import xml.etree.ElementTree as ET

from order.services.common import send_webkassa
from utils.choices import OrderStatusChoices
from utils.custom_logging import save_info, save_warning


def _get_create_order_context(current_site, merchant, instance):
    to_pay_price = f'{int(instance.to_pay_price)*100}'  # if not settings.DEBUG else f'{10000}'
    return {
        'operation': 'CreateOrder',
        'order_type': 'Purchase',
        'merchant': merchant,
        'amount': to_pay_price,
        'currency': '398',
        'order_description': '...',
        'approve_url': f'{current_site}/api/order/payment-success/{instance.id}/',
        'cancel_url': f'{current_site}/api/order/payment-cancel/{instance.id}/',
        'decline_url': f'{current_site}/api/order/payment-decline/{instance.id}/',
        'customer_contact': instance.user.email if instance.user.email else instance.user.phone_number,
    }


def _get_pay_with_token_context(instance, merchant, session_id, payment_order_id):
    to_pay_price = f'{int(instance.to_pay_price)*100}' #if not settings.DEBUG else f'{10000}'
    return {
        'merchant': merchant,
        'order_id': payment_order_id,
        'session_id': session_id,
        'total_price': to_pay_price,
        'currency': 398,
        'card_token': instance.card.card_token,
    }


def _get_create_order_response(context, template_name, url):
    headers = {'Content-Type': 'application/xml'}
    xml = loader.render_to_string(
        template_name,
        context
    )
    save_info(xml)
    resp = requests.post(f'{url}', data=xml, headers=headers)
    save_info(f"{template_name}   -   {resp.text}")
    tree = ET.ElementTree(ET.fromstring(resp.text))
    return tree.find('Response')


def _logging_status(instance, status, fom_file_line):
    text = ''
    if status.text == '10':
        text = "Status: 10 - интернет-магазин не имеет доступа к операции создания заказа " \
               "(или такой интернет-магазин не зарегистрирован);"
    elif status.text == '30':
        text = "Status: 30 - неверный формат сообщения (нет обязательных параметров и т. д.);"
    elif status.text == '54':
        text = "Status: 54 - недопустимая операция;"
    elif status.text == '72':
        text = "Status: 72 - пустой ответ POS-драйвера;"
    elif status.text == '96':
        text = "Status: 96 - системная ошибка;"
    elif status.text == '97':
        text = "Status: 97 - ошибка связи с POS-драйвером;"
    save_warning(f"{fom_file_line} - Order: {instance.id}. {text}")


def pay_with_token(current_site, instance):
    context = _get_create_order_context(current_site, settings.MERCHANT_TOKEN, instance)
    response = _get_create_order_response(context, 'create_token_order.xml', settings.PAYMENT_URL)
    if response is not None:
        first_status = response.find('Status')
        if first_status is None:
            save_warning('FirstStatus is None')
            return False
        if first_status.text != '00':
            _logging_status(instance, first_status, "payment.py 71")
            return False
        order = response.find('Order')
        if order is not None:
            payment_order_id = order.find('OrderID').text
            session_id = order.find('SessionID').text
            url = order.find('URL').text
            if payment_order_id and session_id and url:
                instance.payment_order_id = payment_order_id
                instance.save()
                token_payment_context = _get_pay_with_token_context(instance, settings.MERCHANT_TOKEN, session_id,
                                                                    payment_order_id)
                response = _get_create_order_response(token_payment_context, 'pay_with_token.xml', settings.PAYMENT_URL)
                if response is None:
                    save_warning('No Response')
                    return False
                status = response.find('Status')
                if status is None:
                    save_warning('No Status')
                    return False
                if status.text != '00':
                    _logging_status(instance, status, "payment.py 87")
                    return False
                else:
                    xml_out = response.find('XMLOut')
                    if xml_out is None:
                        save_warning(f'xml_out is NULL')
                        return False
                    save_info(ET.tostring(xml_out))
                    message = xml_out.find('Message')
                    if message is not None:
                        order_status = message.find('OrderStatus')
                        if order_status is None:
                            save_warning('No OrderStatus')
                            return False
                        if order_status.text == 'APPROVED':
                            instance.paid = True
                            instance.is_basket = False
                            instance.status = OrderStatusChoices.NEW
                            instance.save()
                            send_webkassa(instance)
                            save_info(f'Order with id={instance.id}, changed status to PAID')
                            return True
                        save_warning(f'Order status is {order_status.text}')
                        return False
                    save_warning(f'No Message')
                    return False
            save_warning(f'No session id or url')
            return False
        save_warning(f"Order is NULL; {ET.tostring(response, encoding='utf8', method='xml')}")
        return False
    save_warning(f'Response is NULL')
    return False


def pay_with_new_card(current_site, instance):
    context = _get_create_order_context(current_site, settings.MERCHANT_ORDER, instance)
    response = _get_create_order_response(context, 'create_order.xml', settings.PAYMENT_URL)
    if response:
        order = response.find('Order')
        if order:
            payment_order_id = order.find('OrderID').text
            session_id = order.find('SessionID').text
            url = order.find('URL').text
            if payment_order_id and session_id and url:
                instance.payment_order_id = payment_order_id
                instance.save()
                return f'{url}?OrderID={payment_order_id}&SessionID={session_id}'
    return None
