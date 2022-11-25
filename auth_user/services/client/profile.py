from datetime import datetime

import after_response
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from rest_framework.authtoken.models import Token

from auth_user.services.common import send_sms, can_change
from utils.crud import update_object
from utils.current_site import get_current_domain_with_protocol
from utils.email import send_email
from utils.tokens import decode_jwt, create_verification_code, generate_jwt_for_verification

User = get_user_model()


def update_current_user(instance, validated_data):
    return update_object(instance, validated_data)


@after_response.enable
def send_verification_email(token, user, domain):
    context = {
        "domain": domain,
        "token": token,
        "full_name": user.full_name,
        "email": user.new_email,
    }
    send_email([user.new_email], 'Изменение почты', context, 'change_email_v2.html')


def request_email_change(request, instance, validated_data):
    email_token = create_verification_code()
    instance.new_email = validated_data.get('email')
    instance.save()
    current_domain = get_current_domain_with_protocol(request)
    send_verification_email(email_token, instance, current_domain)
    return instance


def _generate_faked_phone_number():
    return str(timezone.now().timestamp())


def delete_account(user, just_inactive=True):
    Token.objects.filter(user=user).delete()
    if just_inactive:
        user.is_active = True
    else:
        old_phone_number = user.phone_number
        user.phone_number = _generate_faked_phone_number()
        user.old_phone_number = old_phone_number
    user.save()


def change_email_from_code(user, validated_data):
    if user.verification_code == validated_data.get('verification_code'):
        if user.new_email:
            user.email = user.new_email
            user.new_email = None
            user.save()
            return user
    raise serializers.ValidationError('VerificationCode is expired')


def change_email_from_token(validated_data):
    token = validated_data.get('token')
    data = decode_jwt(token)
    assert 'datetime' in data and 'email' in data and 'user' in data, (
        '`data` should contains all of this fields: `datetime`, `email`, `user`'
    )
    today = datetime.strptime(data.get('datetime'), '%Y-%m-%d %H:%M:%S')
    if can_change(today):
        try:
            user = User.objects.get(id=data.get('user'))
            user.email = data.get('email')
            user.save()
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError('token expired', code='token_expired')
    raise serializers.ValidationError('token expired', code='token_expired')


def change_email(instance, validated_data):
    instance.email = validated_data.get('email')
    instance.save()
    return instance


def logout(instance):
    Token.objects.filter(user=instance).delete()


def request_change_phone(instance, validated_data):
    new_phone_number = validated_data.get('phone_number')
    instance.verification_code = create_verification_code()
    instance.save()
    send_sms(phone_number=new_phone_number, verification_code=instance.verification_code)

    return generate_jwt_for_verification(instance, new_phone_number), instance
