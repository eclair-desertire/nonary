from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from order.models import Order


@receiver(post_save, sender=Order)
def order_handler(sender, instance, created, **kwargs):
    if created:
        instance.order_id = f"SM-1{str(instance.id).zfill(settings.ORDER_ID_DIGITS)}"
        instance.save()
