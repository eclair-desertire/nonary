from rest_framework import serializers

from auth_user.models import UserCard
from location.models import UserAddress, Post
from order.models import Order
from order.services.client.orders import validate_order_create
from order.services.common import recalculate_total_price, get_order_delivery_address
from promo.models import Promo
from shop.models import Product, Delivery, Payment
from shop.services.client.querysets import get_payment_queryset
from utils.choices import ObjectTypeChoices, DeliveryTypeChoice, DiscountTypeChoices, OrderStatusChoices
from utils.serializers import BaseSerializer


class AddToBasketSerializer(BaseSerializer):
    token = serializers.CharField(required=False, allow_null=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=0)
    city_slug = serializers.CharField(default='almaty')


class AddToBasketResponseSerializer(BaseSerializer):
    token = serializers.CharField()


class ProductSerializer(BaseSerializer):
    version = serializers.CharField()
    barcode = serializers.CharField()
    vendor_code = serializers.CharField()
    weight = serializers.CharField()
    base_unit = serializers.CharField()
    brand = serializers.CharField()
    external_id = serializers.CharField()
    name = serializers.CharField()
    slug = serializers.SerializerMethodField()
    rest = serializers.IntegerField()
    discount_price = serializers.DecimalField(max_digits=14, decimal_places=2)
    price = serializers.DecimalField(max_digits=14, decimal_places=2)
    is_favourite = serializers.BooleanField()
    image = serializers.URLField()

    def get_slug(self, instance):
        if hasattr(instance, 'main_slug'):
            return instance.main_slug
        return instance.slug


class ProductHistorySerializer(BaseSerializer):
    name = serializers.CharField()
    image = serializers.URLField()
    vendor_code = serializers.CharField()


class BasketItemSerializer(BaseSerializer):
    quantity = serializers.IntegerField()
    product = ProductSerializer()
    id = serializers.IntegerField(read_only=True)


class OrderItemHistorySerializer(BasketItemSerializer):
    product = ProductHistorySerializer()
    quantity = serializers.IntegerField()
    product_price = serializers.DecimalField(max_digits=14, decimal_places=2)
    product_original_price = serializers.DecimalField(max_digits=14, decimal_places=2)


class UserSelectedCardSerializer(BaseSerializer):
    id = serializers.IntegerField()
    pan = serializers.CharField()
    brand = serializers.CharField()
    card_token = serializers.CharField()


class BasketDetailSerializer(BaseSerializer):
    id = serializers.IntegerField()
    token = serializers.CharField()
    total_price = serializers.DecimalField(max_digits=14, decimal_places=2)
    item_list = BasketItemSerializer(many=True)


class OrderListHistorySerializer(BaseSerializer):
    id = serializers.IntegerField()
    order_id = serializers.CharField()
    ordered_at = serializers.DateTimeField()
    delivered_at = serializers.DateTimeField()
    status = serializers.ChoiceField(choices=OrderStatusChoices.choices)
    paid = serializers.BooleanField()
    to_pay_price = serializers.DecimalField(max_digits=14, decimal_places=2)
    ticket_url = serializers.URLField()
    ticket_print_url = serializers.URLField()
    has_ticket = serializers.BooleanField()
    product_count = serializers.IntegerField()


class OrderDetailHistorySerializer(OrderListHistorySerializer):
    item_list = OrderItemHistorySerializer(many=True)
    delivery_address = serializers.SerializerMethodField()

    def get_delivery_address(self, instance):
        return get_order_delivery_address(instance)


class CreateOrderSerializer(BaseSerializer):
    payment = serializers.PrimaryKeyRelatedField(queryset=Payment.objects.all())
    comment = serializers.CharField(allow_blank=True)
    is_accept_offer = serializers.BooleanField()
    card = serializers.PrimaryKeyRelatedField(queryset=UserCard.objects.all(), required=False, allow_null=True)

    def validate(self, attrs):
        attrs = super(CreateOrderSerializer, self).validate(attrs)
        if not attrs.get('is_accept_offer', False):
            raise serializers.ValidationError('cannot create order while not accepted!')
        return attrs


class PayOrderSerializer(BaseSerializer):
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())


class ChangeOrderDeliverySerializer(BaseSerializer):
    address = serializers.PrimaryKeyRelatedField(queryset=UserAddress.objects.all(), required=False)
    delivery = serializers.PrimaryKeyRelatedField(queryset=Delivery.objects.all())
    pickup = serializers.PrimaryKeyRelatedField(queryset=Post.objects.filter(object_type=ObjectTypeChoices.PICKUP),
                                                required=False)
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.filter(object_type=ObjectTypeChoices.POST),
                                              required=False)

    def validate(self, attrs):
        attrs = super(ChangeOrderDeliverySerializer, self).validate(attrs)
        return validate_order_create(attrs)


class AddPromoToOrderSerializer(BaseSerializer):
    token = serializers.CharField(required=False, allow_null=True)
    promo = serializers.PrimaryKeyRelatedField(queryset=Promo.objects.all())

    def validate(self, attrs):
        attrs = super(AddPromoToOrderSerializer, self).validate(attrs)
        try:
            order = Order.objects.get(token=attrs.get('token'), is_basket=True)
            attrs.update({
                'order': order
            })
            return attrs
        except Order.DoesNotExist:
            raise serializers.ValidationError('not found')


class ProductAddSerializer(BaseSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField()


class ProductRestSerializer(BaseSerializer):
    product_ids = serializers.ListSerializer(
        child=serializers.IntegerField()
    )


class OrderCreateSerializer(BaseSerializer):
    goods = ProductAddSerializer(many=True)
    comment = serializers.CharField(allow_blank=True)
    promo = serializers.PrimaryKeyRelatedField(queryset=Promo.objects.all())

    address = serializers.PrimaryKeyRelatedField(queryset=UserAddress.objects.all(), required=False)
    delivery = serializers.PrimaryKeyRelatedField(queryset=Delivery.objects.all())
    payment = serializers.PrimaryKeyRelatedField(queryset=Payment.objects.all())
    is_accept_offer = serializers.BooleanField()

    pickup = serializers.PrimaryKeyRelatedField(queryset=Post.objects.filter(object_type=ObjectTypeChoices.PICKUP),
                                                required=False)
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.filter(object_type=ObjectTypeChoices.POST),
                                              required=False)

    def validate(self, attrs):
        attrs = super(OrderCreateSerializer, self).validate(attrs)
        return validate_order_create(attrs)


class OrderPriceInfoSerializer(BaseSerializer):
    products_total_price = serializers.SerializerMethodField()
    product_count = serializers.IntegerField()
    delivery = serializers.SerializerMethodField()
    discount = serializers.SerializerMethodField()
    promo_value = serializers.SerializerMethodField()
    to_pay_price = serializers.DecimalField(max_digits=14, decimal_places=2)
    selected_card = serializers.SerializerMethodField()

    def get_selected_card(self, instance):
        if instance.user and instance.user.selected_card:
            return UserSelectedCardSerializer(instance.user.selected_card, context=self.context).data
        return None

    def get_delivery(self, instance):
        return instance.delivery.price if instance.delivery else 0

    def get_products_total_price(self, instance):
        _, original_price = recalculate_total_price(instance)
        return original_price

    def get_discount(self, instance):
        total_price, original_price = recalculate_total_price(instance)
        discount = original_price - total_price
        return discount

    def get_promo_value(self, instance):
        if instance.promo:
            total_price, _ = recalculate_total_price(instance)
            return total_price - instance.to_pay_price
        return 0.0


class OrderPriceInfoSerializerResponse(OrderPriceInfoSerializer):
    selected_card = UserSelectedCardSerializer()


class OrderDetailSerializer(BaseSerializer):
    id = serializers.IntegerField()
    order_id = serializers.CharField()
    delivery_address = serializers.SerializerMethodField()
    to_pay_price = serializers.DecimalField(max_digits=14, decimal_places=2)
    phone_number = serializers.SerializerMethodField()

    def get_delivery_address(self, instance):
        return get_order_delivery_address(instance)

    def get_phone_number(self, instance):
        if instance.user:
            return instance.user.phone_number
        return ''


class CopyOrderSerializer(BaseSerializer):
    order = serializers.IntegerField()


class LastOrderSerializer(BaseSerializer):
    id = serializers.IntegerField()
    delivery_type = serializers.CharField()
    address = serializers.SerializerMethodField()

    def get_address(self, instance):
        if instance.delivery_type == DeliveryTypeChoice.COURIER:
            return f"{instance.order_id}"
        return instance.only_street

