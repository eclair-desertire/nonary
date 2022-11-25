from django.apps import apps
from django.db.models import Prefetch
from django.template import loader

from utils.choices import OrderStatusChoices

Order = apps.get_model(app_label='order', model_name='Order')
OrderItem = apps.get_model(app_label='order', model_name='OrderItem')


def get_orders_for_export(filter_lookup, exclude_lookup):
    qs = Order.objects.filter(**filter_lookup).prefetch_related(
        Prefetch(
            'items',
            queryset=OrderItem.objects.filter(**{}).select_related(
                'product'
            ).distinct(),
            to_attr='item_list'
        )
    ).select_related(
        'address', 'pickup', 'post', 'address__address', 'pickup__pickup', 'post__post',
        'address__address__city', 'pickup__pickup__city', 'post__post__city'
    ).exclude(**exclude_lookup).distinct()
    return qs


def get_export_context(orders):
    context = {
        'orders': orders
    }
    return context


def get_export_order_xml():
    orders = get_orders_for_export(
        {'is_basket': False, 'delivery__isnull': False, 'status': OrderStatusChoices.NEW},
        {}
    )
    context = get_export_context(orders)
    xml = loader.render_to_string(
        'orders.xml',
        context
    )
    return xml
