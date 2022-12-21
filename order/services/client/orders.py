from django.apps import apps
from django.contrib.sessions.backends.db import SessionStore
from django.db.models import Prefetch, Sum, Case, When, Value, BooleanField
from django.db.transaction import atomic
from django.utils import timezone
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from order.services.common import recalculate_to_pay_price, recalculate_total_price
from utils.choices import DeliveryTypeChoice, StorehouseTypeChoices, OrderStatusChoices
from utils.custom_logging import save_info

Order = apps.get_model(app_label='order', model_name="Order")
OrderItem = apps.get_model(app_label='order', model_name="OrderItem")
OrderDeliverAddress = apps.get_model(app_label='order', model_name="OrderDeliverAddress")
OrderDeliverPickup = apps.get_model(app_label='order', model_name="OrderDeliverPickup")
OrderDeliverPost = apps.get_model(app_label='order', model_name="OrderDeliverPost")


def assign_user_to_order(user, validated_data):

    baskets = Order.objects.filter(is_basket=True, **validated_data).select_related(
        'delivery', 'promo', 'address', 'address__address', 'address__address__city', 'user', 'user__selected_card',
        'pickup', 'pickup__pickup', 'pickup__pickup__city', 'post', 'post__post', 'post__post__city',
    )

    basket = get_object_or_404(baskets, **validated_data)
    basket.delivery = None
    basket.promo = None

    OrderDeliverPickup.objects.filter(order=basket).delete()
    OrderDeliverPost.objects.filter(order=basket).delete()
    OrderDeliverAddress.objects.filter(order=basket).delete()

    total_price, original_price = recalculate_total_price(basket)
    if basket.delivery:
        total_price += basket.delivery.price
    basket.original_price = original_price
    basket.total_price = total_price
    basket.to_pay_price = recalculate_to_pay_price(basket, total_price)

    basket.user = user
    basket.save()


def create_order_deliveries(validated_data, order):
    with atomic():
        for key, value in validated_data.items():
            if key in ['delivery', 'payment', 'comment', 'is_accept_offer']:
                setattr(order, key, value)
            else:
                if key == 'address' and validated_data.get('delivery').delivery_type == DeliveryTypeChoice.COURIER:
                    OrderDeliverPickup.objects.filter(order=order).delete()
                    OrderDeliverPost.objects.filter(order=order).delete()
                    OrderDeliverAddress.objects.filter(order=order).delete()
                    OrderDeliverAddress.objects.get_or_create(order=order, address=value)
                elif key == 'pickup' and validated_data.get('delivery').delivery_type == DeliveryTypeChoice.PICKUP:
                    OrderDeliverAddress.objects.filter(order=order).delete()
                    OrderDeliverPost.objects.filter(order=order).delete()
                    OrderDeliverPickup.objects.filter(order=order).delete()
                    OrderDeliverPickup.objects.get_or_create(order=order, pickup=value)
                elif key == 'post' and validated_data.get('delivery').delivery_type == DeliveryTypeChoice.POST:
                    OrderDeliverPickup.objects.filter(order=order).delete()
                    OrderDeliverPost.objects.filter(order=order).delete()
                    OrderDeliverAddress.objects.filter(order=order).delete()
                    OrderDeliverPost.objects.get_or_create(order=order, post=value)
        order.save()


def change_order_delivery(user, token, validated_data):
    baskets = Order.objects.filter(is_basket=True, **{'token': token, 'user': user}).select_related(
        'delivery', 'promo', 'address', 'address__address', 'address__address__city', 'user', 'user__selected_card',
        'pickup', 'pickup__pickup', 'pickup__pickup__city', 'post', 'post__post', 'post__post__city',
    )
    order = get_object_or_404(baskets, **{'token': token, 'user': user})
    create_order_deliveries(validated_data, order)
    total_price, original_price = recalculate_total_price(order)
    if order.delivery:
        total_price += order.delivery.price
    order.original_price = original_price
    order.total_price = total_price
    order.to_pay_price = recalculate_to_pay_price(order, total_price)
    order.save()
    return order


def create_order(user, token, validated_data):
    baskets = Order.objects.filter(is_basket=True, **{'token': token, 'user': user})
    order = get_object_or_404(baskets, **{'token': token, 'user': user})
    items = OrderItem.objects.filter(order=order).select_related('product')
    moment = timezone.now() - timezone.timedelta(minutes=30)

    for item in items:
        ordered_items_count = OrderItem.objects.filter(
            product=item.product,
            order__is_basket=True,
            order__city_slug=order.city_slug,
            order__updated_at__gte=moment
        ).exclude(order=order).distinct().count()
        rest = item.product.rests_dict.get(f'{order.city_slug}_{StorehouseTypeChoices.DISCOUNT}')
        if rest - item.quantity - ordered_items_count < 0:
            raise serializers.ValidationError('Некоторых товаров из корзины больше нет в наличий!')

    order.is_basket = False
    order.ordered_at = timezone.now()
    for key, value in validated_data.items():
        if key in ['delivery', 'payment', 'comment', 'is_accept_offer', 'card']:
            setattr(order, key, value)
    order.save()
    return order


def add_promo(user, validated_data):
    order = validated_data.get('order')
    promo = validated_data.get('promo')
    if Order.objects.filter(is_basket=False, promo=promo, user=user).exclude(id=order.id).exists():
        raise serializers.ValidationError('already used')
    if 0 < promo.max_order_price < order.total_price:
        raise serializers.ValidationError('max_order_price')
    if order.total_price < promo.min_order_price:
        raise serializers.ValidationError('min_order_price')
    order.promo = promo
    order.to_pay_price = recalculate_to_pay_price(order, order.total_price)
    order.save()
    return order


def get_order_history(user):
    orders = Order.objects.filter(
        is_basket=False, user=user
    ).annotate(
        has_ticket=Case(
            When(ticket_url__isnull=False, then=Value(True, output_field=BooleanField())),
            default=Value(False, output_field=BooleanField())
        ),
        product_count=Sum('items__quantity')
    )
    return orders.distinct().order_by('-updated_at')


def get_order_by_id(pk):
    qs = Order.objects.filter(pk=pk).select_related('user')
    return get_object_or_404(qs, **{'pk': pk})


def validate_order_create(attrs):
    delivery = attrs.get('delivery')
    if delivery.delivery_type == DeliveryTypeChoice.COURIER:
        if not attrs.get('address'):
            raise serializers.ValidationError('`address` is required if `courier` chosen')
    elif delivery.delivery_type == DeliveryTypeChoice.POST:
        if not attrs.get('post'):
            raise serializers.ValidationError('`post` is required if `post` chosen')
    elif delivery.delivery_type == DeliveryTypeChoice.POST:
        if not attrs.get('pickup'):
            raise serializers.ValidationError('`pickup` is required if `pickup` chosen')
    return attrs


def create_order_without_basket(validated_data, user):
    order = Order.objects.create(user=user, is_basket=False, comment=validated_data.get('comment'),
                                 is_accept_offer=validated_data.get('is_accept_offer', False))
    create_order_deliveries(validated_data, order)
    order_items = [OrderItem(**item) for item in validated_data.get('goods', [])]
    OrderItem.objects.bulk_create(order_items)
    total_price, original_price = recalculate_total_price(order)
    if order.delivery:
        total_price += order.delivery.price
    order.original_price = original_price
    order.total_price = total_price
    order.payment_order_id = order.order_id
    order.to_pay_price = recalculate_to_pay_price(order, total_price)
    order.save()
    return order


def get_order_for_calculation_info(filter_lookup):
    order = Order.objects.filter(**filter_lookup).select_related(
        'delivery', 'promo', 'address', 'address__address', 'address__address__city', 'user', 'user__selected_card',
        'pickup', 'pickup__pickup', 'pickup__pickup__city', 'post', 'post__post', 'post__post__city',
    ).annotate(
        product_count=Sum('items__quantity')
    )
    return order.first()


def prefetch_order_history(queryset):
    return queryset.select_related(
        'address', 'pickup', 'post', 'address__address', 'pickup__pickup', 'post__post',
        'address__address__city', 'pickup__pickup__city', 'post__post__city'
    ).prefetch_related(
        Prefetch(
            'items',
            queryset=OrderItem.objects.order_by().select_related('product'),
            to_attr='item_list'
        )
    )


def copy_order(instance):
    session = SessionStore()
    session.save(must_create=True)
    basket = Order.objects.create(
        token=session.session_key, user=instance.user, delivery=instance.delivery
    )
    if hasattr(instance, 'address') and instance.address:
        OrderDeliverAddress.objects.create(order=basket, address=instance.address.address)
    elif hasattr(instance, 'pickup') and instance.pickup:
        OrderDeliverPickup.objects.create(order=basket, pickup=instance.pickup.pickup)
    elif hasattr(instance, 'post') and instance.post:
        OrderDeliverPost.objects.create(order=basket, post=instance.post.post)
    assert hasattr(instance, 'item_list'), 'Order object should contains `item_list`'
    order_items = []
    for item in instance.item_list:
        order_items.append(OrderItem(order=basket, product=item.product, quantity=item.quantity))
    OrderItem.objects.bulk_create(order_items)
    total_price, original_price = recalculate_total_price(basket)
    if basket.delivery:
        total_price += basket.delivery.price
    basket.original_price = original_price
    basket.total_price = total_price
    basket.to_pay_price = recalculate_to_pay_price(basket, total_price)
    basket.save()
    return basket
