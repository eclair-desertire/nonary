from datetime import datetime
from typing import OrderedDict

from django.db.models import F, Q, Count
from django.apps import apps
from django.utils import timezone
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from utils.crud import get_object_by_lookup, create_object, get_object_queryset

Promo = apps.get_model(app_label='promo', model_name='Promo')
UserSelectedPromo = apps.get_model(app_label='promo', model_name='UserSelectedPromo')


def add_promo(filter_lookup: OrderedDict, user):
    today = datetime.now().date()
    qs = Promo.objects.filter((Q(activate_from__lte=today) & Q(activate_to__gte=today)) | Q(permanent=True))
    instance = get_object_or_404(qs, **filter_lookup)
    if instance is not None:
        if not UserSelectedPromo.objects.filter(user=user, promo=instance).exists():
            create_object('promo', 'UserSelectedPromo', {'user': user, 'promo': instance, 'selected': True})
        return instance
    raise serializers.ValidationError('Промокод не найден', code='not_found')


def get_selected_promo(user):
    return get_object_queryset('promo', 'Promo', {'users__user': user}).annotate(
        selected=F('users__selected')
    ).distinct()


def get_promo_list(user, is_auto=True):
    today = timezone.now().date()
    filter_kwargs = {'is_active': True}
    if is_auto:
        filter_kwargs.update({
            'used_count': 0
        })
    qs = Promo.objects.annotate(
        used_count=Count('orders__id', filter=Q(orders__user=user) & Q(orders__is_basket=False)),
    ).filter(((Q(activate_from__lte=today) & Q(activate_to__gte=today)) | Q(permanent=True)) &
             (Q(is_auto=is_auto) | Q(users__user=user)), **filter_kwargs)
    return qs.distinct()


def select_promo(instance):
    instance.selected = True
    instance.save()
    return instance
