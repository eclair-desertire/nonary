import math
import random
from datetime import datetime

from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import jwt
from django.utils.crypto import get_random_string


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        user.timestamp = timestamp
        user.save()
        return f"{user.pk}{user.verification_code}{timestamp}{user.is_active}"


account_activation_token = TokenGenerator()

password_reset_token = PasswordResetTokenGenerator()


def generate_jwt_for_verification(user, phone_number=None):
    if phone_number is None:
        phone_number = user.phone_number
    today = datetime.now()
    return jwt.encode(
        {
            "user": user.id,
            "verification_code": user.verification_code,
            "phone_number": phone_number,
            "datetime": today.strftime('%Y-%m-%d %H:%M:%S')
        },
        "secret", algorithm="HS256"
    )


def decode_jwt(token):
    return jwt.decode(token, "secret", algorithms=["HS256"])


def generate_password():
    length = 10
    allowed_chars = "abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return get_random_string(length, allowed_chars)


def create_verification_code():
    digits = "0123456789"
    verification_code = ""
    for i in range(4):
        verification_code += digits[math.floor(random.random() * 10)]
    return verification_code if settings.IS_SEND_SMS else '1111'
