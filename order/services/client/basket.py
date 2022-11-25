from django.apps import apps
from django.contrib.sessions.backends.db import SessionStore
from django.db.models import Prefetch, Value, BooleanField, Case, When, F
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from order.services.common import recalculate_total_price, recalculate_to_pay_price
from utils.choices import StorehouseTypeChoices
from utils.custom_logging import save_info

Order = apps.get_model(app_label='order', model_name="Order")
OrderItem = apps.get_model(app_label='order', model_name="OrderItem")
Rest = apps.get_model(app_label='shop', model_name="Rest")
ProductPrice = apps.get_model(app_label='shop', model_name="ProductPrice")
Product = apps.get_model(app_label='shop', model_name="Product")


def add_product_to_basket(user, validated_data):
    product = validated_data.get('product')
    city_slug = validated_data.get('city_slug')
    product_count = product.rests_dict.get(f'{city_slug}_{StorehouseTypeChoices.DISCOUNT}')
    moment = timezone.now() - timezone.timedelta(minutes=30)
    order_token = validated_data.get('token')
    ordered_items_count = OrderItem.objects.filter(
        product=validated_data.get('product'),
        order__is_basket=True,
        order__city_slug=city_slug,
        order__updated_at__gte=moment
    ).distinct()
    if order_token:
        ordered_items_count = ordered_items_count.exclude(order__token=order_token)
    ordered_items_count = ordered_items_count.count()
    if product_count - ordered_items_count - validated_data.get('quantity', 0) < 0:
        raise serializers.ValidationError('Товар закончился!')
    if validated_data.get('token'):
        try:
            basket = Order.objects.get(token=validated_data.get('token'))
        except Order.DoesNotExist:
            current_user = None
            if user.is_authenticated:
                current_user = user
            session = SessionStore()
            session.save(must_create=True)
            basket = Order.objects.create(token=session.session_key, user=current_user, city_slug=city_slug)
    else:
        current_user = None
        if user.is_authenticated:
            current_user = user
        session = SessionStore()
        session.save(must_create=True)
        basket = Order.objects.create(token=session.session_key, user=current_user, city_slug=city_slug)
    item, _ = OrderItem.objects.get_or_create(order=basket, product=validated_data.get('product'))
    if validated_data.get('quantity') == 0:
        item.delete()
    else:
        item.quantity = validated_data.get('quantity')
        item.save()
    total_price, original_price = recalculate_total_price(basket)
    if basket.delivery:
        total_price += basket.delivery.price
    basket.original_price = original_price
    basket.total_price = total_price
    basket.to_pay_price = recalculate_to_pay_price(basket, total_price)
    basket.save()
    return basket


def get_basket_info(token, user, city_slug=None):
    # product_rest_subquery = Rest.objects.filter(
    #     product_id=OuterRef('pk'),
    #     storehouse__storehouse_type=StorehouseTypeChoices.DISCOUNT,
    #     storehouse__cities__slug=city_slug,
    # ).values('quantity')[:1]
    # product_discount_price_subquery = ProductPrice.objects.filter(
    #     product_id=OuterRef('pk'),
    #     storehouse__storehouse_type=StorehouseTypeChoices.DISCOUNT,
    #     storehouse__cities__slug=city_slug,
    # ).values('price')[:1]
    # product_price_subquery = ProductPrice.objects.filter(
    #     product_id=OuterRef('pk'),
    #     storehouse__storehouse_type=StorehouseTypeChoices.BASIC,
    #     storehouse__cities__slug=city_slug,
    # ).values('price')[:1]
    is_favourite_annotate = Value(False, output_field=BooleanField())
    if user.is_authenticated:
        is_favourite_annotate = Case(
            When(
                favourites__user=user, then=Value(True, output_field=BooleanField())
            ), default=Value(False, output_field=BooleanField()),
            output_field=BooleanField()
        )
    baskets = Order.objects.filter(token=token).select_related(
        'user', 'user__selected_card'
    ).prefetch_related(
        Prefetch(
            'items',
            queryset=OrderItem.objects.order_by().prefetch_related(
                Prefetch(
                    'product',
                    queryset=Product.objects.annotate(
                        rest=F(f'rests_dict__{city_slug}_{StorehouseTypeChoices.DISCOUNT}'),
                        price=F(f'prices_dict__{city_slug}_{StorehouseTypeChoices.BASIC}'),
                        discount_price=F(f'prices_dict__{city_slug}_{StorehouseTypeChoices.DISCOUNT}'),
                        is_favourite=is_favourite_annotate,
                        main_slug=Case(
                            When(main_products__isnull=False, then=F('main_products__slug')),
                            default=F('slug')
                        )
                    )
                )
            ),
            to_attr='item_list'
        )
    )
    return baskets


def clear_basket(token):
    order_items = OrderItem.objects.filter(order__token=token, order__is_basket=True)
    if order_items.exists():
        order_items.delete()
    else:
        raise PermissionDenied
