import json
from datetime import datetime
import xml.etree.ElementTree as ET

import requests
from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

BadSMS = apps.get_model(app_label='auth_user', model_name='BadSMS')
UserCard = apps.get_model(app_label='auth_user', model_name='UserCard')


def send_sms(phone_number=None, verification_code=None):
    assert phone_number is not None, '`phone_number` is requred'
    assert verification_code is not None, '`verification_code` is requred'
    url = f"https://api.smstraffic.ru/multi.php"
    send_data = {
        'login': settings.SMS_LOGIN,
        'password': settings.SMS_PASS,
        'phones': phone_number,
        'message': f"Код для авторизации: {verification_code}",
        'rus': 5,
        'originator': 'Tvoy.kz'
    }
    resp = requests.post(url, data=send_data)
    try:
        resp_data = resp.text
        tree = ET.ElementTree(ET.fromstring(resp_data))
        result = tree.find('result').text
        code = tree.find('code').text
        description = tree.find('description').text
        if result != 'OK' or code != '0':
            BadSMS.objects.create(phone_number=phone_number, code=verification_code, description=description)
    except Exception as _:
        BadSMS.objects.create(phone_number=phone_number, code=verification_code)


def can_change(requested_datetime, token_lifetime_in_minutes=settings.TOKEN_LIFETIME_IN_MINUTES):
    today = datetime.now()
    return (today - requested_datetime).total_seconds() <= token_lifetime_in_minutes * 60


def create_user_card_token(user_id, pan, brand, card_token):
    try:
        user = User.objects.get(id=user_id)
        UserCard.objects.create(user=user, pan=pan, brand=brand, card_token=card_token)
    except User.DoesNotExist:
        return


def delete_user_card_token(instance):
    instance.delete()

