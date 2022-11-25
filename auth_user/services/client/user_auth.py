import json
from datetime import datetime

import requests
from django.conf import settings
from django.apps import apps
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from auth_user.services.common import send_sms, can_change
from utils.tokens import generate_jwt_for_verification, decode_jwt, create_verification_code

User = get_user_model()
BadSMS = apps.get_model(app_label='auth_user', model_name='BadSMS')


def _register(validated_data):
    user = User.objects.create_user(**validated_data)
    return generate_jwt_for_verification(user), user.verification_code, user


def _login(user):
    user.verification_code = create_verification_code()
    user.save()
    return generate_jwt_for_verification(user), user.verification_code


def auth(validated_data):
    try:
        user = User.objects.get(phone_number=validated_data.get('phone_number'))
        # if we don't delete user from database, just setting not active
        if not user.is_active:
            user.is_active = True
            user.save()
        token, verification_code = _login(user)
    except User.DoesNotExist:
        token, verification_code, user = _register(validated_data)
    if settings.IS_SEND_SMS:
        send_sms(phone_number=user.phone_number, verification_code=verification_code)
    return token, user


def verify_code(validated_data):
    decoded_token = decode_jwt(validated_data.get('token'))

    assert 'datetime' in decoded_token and 'verification_code' in decoded_token and 'user' in decoded_token and \
           'phone_number' in decoded_token, '`decoded_token` should contains all of this fields: `user`, ' \
                                            '`verification_code`, `phone_number`, `datetime` '
    today = datetime.strptime(decoded_token.get('datetime'), '%Y-%m-%d %H:%M:%S')
    if validated_data.get('verification_code') == decoded_token.get('verification_code') and can_change(today):
        try:
            user = User.objects.get(pk=decoded_token.get('user'),
                                    verification_code=validated_data.get('verification_code'))
            user.phone_number = decoded_token.get('phone_number')
            user.save()
            # Token.objects.filter(user=user).delete()
            token, _ = Token.objects.get_or_create(user=user)
            return token, user
        except User.DoesNotExist:
            raise serializers.ValidationError('Неверный код!', code='invalid_code')
    raise serializers.ValidationError('Неверный код!', code='invalid_code')
