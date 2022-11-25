from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

from utils.choices import OrderStatusChoices, ObjectTypeChoices, DeliveryTypeChoice, PaymentTypeChoice
from utils.models import BaseModel
from utils.statics import ORDER_KEYS, DELIVERY_KEYS

User = get_user_model()


class Order(BaseModel):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='orders',
                             verbose_name='Пользователь')
    status = models.CharField(max_length=20, choices=OrderStatusChoices.choices,
                              default=OrderStatusChoices.NOT_FINISHED,
                              verbose_name='Статус')
    delivered_at = models.DateTimeField(blank=True, null=True, verbose_name='Доставлен')
    total_price = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Итого', default=0.0)
    original_price = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Цена без скидки', default=0.0)
    to_pay_price = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='К оплате', default=0.0)
    is_basket = models.BooleanField(default=True, verbose_name='Корзина?')
    token = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Токен')
    delivery = models.ForeignKey('shop.Delivery', on_delete=models.SET_NULL, blank=True, null=True,
                                 verbose_name='Способ доставки')
    payment = models.ForeignKey('shop.Payment', on_delete=models.SET_NULL, blank=True, null=True,
                                verbose_name='Способ оплаты')
    comment = models.TextField(blank=True, default='', verbose_name='Комментарии к заказу')
    promo = models.ForeignKey('promo.Promo', on_delete=models.PROTECT, related_name='orders', verbose_name='Промокод',
                              blank=True, null=True)
    is_accept_offer = models.BooleanField(default=False)
    ordered_at = models.DateTimeField(null=True)
    paid = models.BooleanField(default=False, verbose_name='Оплачено?')
    payment_order_id = models.CharField(max_length=1024, blank=True, null=True)
    order_id = models.CharField(max_length=255, null=True)
    card = models.ForeignKey('auth_user.UserCard', on_delete=models.SET_NULL, null=True)
    ticket_url = models.URLField(null=True, verbose_name='Ссылка чека')
    ticket_print_url = models.URLField(null=True, verbose_name='Ссылка чека(Print)')
    city_slug = models.CharField(max_length=255, default='almaty')

    @property
    def payment_status(self):
        if self.payment.payment_type in [PaymentTypeChoice.CASH, PaymentTypeChoice.POS]:
            return "N"
        else:
            if self.status == OrderStatusChoices.NEW:
                return "O"
            if not self.paid:
                return "N"
            return "O"

    @property
    def delivery_method(self):
        return DELIVERY_KEYS[self.delivery.delivery_type]

    @property
    def payment_type(self):
        return self.payment.get_payment_type_display()

    @property
    def delivery_commerce_id(self):
        commerce_id = ''
        if hasattr(self, 'address') and self.address and self.delivery and \
                self.delivery.delivery_type == DeliveryTypeChoice.COURIER:
            commerce_id = self.delivery.commerceml_id
        elif hasattr(self, 'pickup') and self.pickup:
            commerce_id = self.pickup.pickup.commerceml_id
        elif hasattr(self, 'post') and self.post:
            commerce_id = self.post.post.commerceml_id
        return commerce_id if commerce_id is not None else ''

    @property
    def delivery_address(self):
        address = ''
        if hasattr(self, 'address') and self.address:
            address = self.address.address.full_address
        elif hasattr(self, 'pickup') and self.pickup:
            address = self.pickup.pickup.full_address
        elif hasattr(self, 'post') and self.post:
            address = self.post.post.full_address
        return address

    @property
    def only_street(self):
        if hasattr(self, 'address') and self.address:
            return self.address.address.only_street
        elif hasattr(self, 'pickup') and self.pickup:
            return self.pickup.pickup.only_street
        elif hasattr(self, 'post') and self.post:
            return self.post.post.only_street
        return ''

    @property
    def order_status(self):
        return ORDER_KEYS[self.status]

    def __str__(self):
        return f"Заказ {self.order_id}"

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class OrderDeliverAddress(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='address')
    address = models.ForeignKey('location.UserAddress', on_delete=models.CASCADE, related_name='orders')


class OrderDeliverPickup(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='pickup')
    pickup = models.ForeignKey('location.Post', on_delete=models.CASCADE, related_name='pickup_orders',
                               limit_choices_to={'object_type': ObjectTypeChoices.PICKUP, 'is_active': True})


class OrderDeliverPost(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='post')
    post = models.ForeignKey('location.Post', on_delete=models.CASCADE, related_name='post_orders',
                             limit_choices_to={'object_type': ObjectTypeChoices.POST, 'is_active': True})


class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    product = models.ForeignKey('shop.Product', on_delete=models.PROTECT, related_name='orders', verbose_name='Товар')
    quantity = models.IntegerField(default=1, verbose_name='Количество')
    product_price = models.DecimalField(max_digits=14, decimal_places=2, default=0.0)
    product_original_price = models.DecimalField(max_digits=14, decimal_places=2, default=0.0)


class WebkassaToken(BaseModel):
    token = models.CharField(max_length=10000)

    class Meta:
        ordering = ('created_at', )
