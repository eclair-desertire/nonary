from django_filters import rest_framework as filters

from order.models import Order


class HistoryFilter(filters.FilterSet):
    to_pay_price_min = filters.NumberFilter(field_name='to_pay_price', lookup_expr='gte')
    to_pay_price_max = filters.NumberFilter(field_name='to_pay_price', lookup_expr='lte')
    created_at_after = filters.DateFilter(field_name='created_at', lookup_expr='date__gte')
    created_at_before = filters.DateFilter(field_name='created_at', lookup_expr='date__lte')

    class Meta:
        model = Order
        fields = ('status', 'to_pay_price_min', 'to_pay_price_max', 'created_at_after', 'created_at_before')
