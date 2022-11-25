from django.contrib import admin
from order.models import Order, OrderItem
from order.services.common import get_order_delivery_address, get_order_user_data
from utils.choices import DiscountTypeChoices


class OrderItemTabular(admin.TabularInline):
    model = OrderItem
    verbose_name = 'Детали заказа'
    verbose_name_plural = 'Детали заказа'
    readonly_fields = ('product', 'quantity',)
    fields = ('product', 'quantity', )
    can_delete = False

    def get_max_num(self, request, obj=None, **kwargs):
        """Hook for customizing the max number of extra inline forms."""
        return OrderItem.objects.filter(order=obj).count()


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'get_delivery_address', 'total_price', 'created_at', 'delivered_at', 'status',
                    'payment_order_id',)
    list_display_links = ('order_id', 'user', 'get_delivery_address', 'total_price', 'created_at', 'delivered_at',)
    list_filter = ('status', )

    inlines = (OrderItemTabular, )

    def has_add_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_delivery_address(self, obj):
        return get_order_delivery_address(obj)

    def get_phone_number(self, obj):
        return get_order_user_data('phone_number', obj)

    def get_email(self, obj):
        return get_order_user_data('email', obj)

    def get_payment_type(self, obj):
        return obj.payment_type

    def get_delivery_type(self, obj):
        if obj.delivery:
            return obj.delivery.get_delivery_type_display()
        return ''

    def get_discount_amount(self, obj):
        if obj.promo:
            if obj.promo.discount_type == DiscountTypeChoices.FIXED:
                return obj.promo.value
            return obj.total_price * obj.promo.value / 100
        return 0

    get_delivery_address.short_description = 'Адрес'
    get_phone_number.short_description = 'Номер телефона'
    get_email.short_description = 'Email'
    get_payment_type.short_description = 'Способ оплаты'
    get_delivery_type.short_description = 'Способ доставки'
    get_discount_amount.short_description = 'Сумма скидки'

    fieldsets = (
        (None, {'fields': ('status', 'paid', 'user', 'get_phone_number', 'get_email', 'get_delivery_address',
                           'total_price', 'to_pay_price', 'comment', 'created_at', 'delivered_at', 'ticket_url',
                           'ticket_print_url', 'get_payment_type', 'get_delivery_type', 'get_discount_amount',
                           )}),
    )

    readonly_fields = (
        'user', 'get_phone_number', 'get_email', 'get_delivery_address', 'total_price', 'delivered_at', 'created_at',
        'status', 'to_pay_price', 'comment', 'paid', 'ticket_url', 'ticket_print_url', 'get_payment_type',
        'get_delivery_type', 'get_discount_amount',
    )

    def get_queryset(self, request):
        qs = super(OrderAdmin, self).get_queryset(request).select_related(
            'user', 'address', 'address__address', 'address__address__city',
            'post', 'post__post', 'post__post__city', 'promo',
            'pickup', 'pickup__pickup', 'pickup__pickup__city',
        )
        return qs.filter(is_basket=False)
