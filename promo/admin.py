from django.contrib import admin
from django.db.models import Count, Q

from promo.models import Promo
from utils.choices import OrderStatusChoices


@admin.register(Promo)
class PromoAdmin(admin.ModelAdmin):
    list_display = ('name', 'activate_from', 'activate_to', 'created_at', 'permanent', 'get_used_count')
    list_display_links = ('name', 'activate_from', 'activate_to', 'created_at', 'permanent', 'get_used_count')
    list_filter = ('permanent', )
    search_fields = ('name', )

    def get_used_count(self, obj):
        return obj.used_count
    get_used_count.short_description = 'Количество использований'
    get_used_count.allow_tags = True
    get_used_count.admin_order_field = 'used_count'

    def get_queryset(self, request):
        queryset = super(PromoAdmin, self).get_queryset(request)
        queryset = queryset.annotate(
            used_count=Count(
                'orders__id',
                filter=Q(orders__is_basket=False) & Q(orders__status__in=[
                    OrderStatusChoices.NOT_FINISHED,
                    OrderStatusChoices.NEW,
                    OrderStatusChoices.PROCESSING,
                    OrderStatusChoices.IN_STOCK,
                    OrderStatusChoices.STAFFED,
                    OrderStatusChoices.DELIVER_DEPARTMENT,
                    OrderStatusChoices.IN_DELIVER,
                    OrderStatusChoices.DELIVERED,
                    OrderStatusChoices.COMPLETED,
                ]), distinct=True)
        )
        return queryset
