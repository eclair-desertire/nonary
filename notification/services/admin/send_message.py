from django.conf import settings
from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message, Notification as FCMNotification, Notification

from utils.custom_logging import save_info


def send_message(title, body=None, image=None):
    image_url = ''
    if image:
        image_url = f"{settings.CURRENT_SITE}/{image.url}"
    if body is None:
        body = ''
    message = Message(notification=FCMNotification(title=title, body=body, image=image_url))
    device = FCMDevice.objects.filter(active=True)
    device.send_message(message)


def send_notification(data, notification):
    message = Message(data=data, notification=Notification(**notification))
    device = FCMDevice.objects.filter(active=True)
    device.send_message(message)
