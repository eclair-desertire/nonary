from datetime import datetime

from django.db.models import Case, When, Value, BooleanField, Count, Q, F, CharField, Sum

from utils.choices import StorehouseTypeChoices
from utils.crud import get_object_queryset


def get_stock_queryset(action, city_slug):
    qs = get_object_queryset(app_label='main_page', model_name='Stock',
                             filter_lookup={'is_active': True}).order_by('-deadline')
    if action == 'retrieve':
        qs = qs.annotate(
            product_count=Count(
                'products__id',
                filter=Q(products__is_active=True) &
                       Q(**{f'products__rests_dict__{city_slug}_{StorehouseTypeChoices.DISCOUNT}__gt': 0}),
                distinct=True)
        )
    return qs


def get_story_queryset(user, filter_lookup):
    viewed_annotate = Value(False, output_field=BooleanField())
    if user.is_authenticated:
        viewed_annotate = Case(
            When(viewed_users__user=user, then=Value(True, output_field=BooleanField())),
            default=Value(False, output_field=BooleanField())
        )
    return get_object_queryset(
        app_label='main_page', model_name='Story', filter_lookup=filter_lookup
    ).annotate(
        viewed=viewed_annotate,
        category_slug=F('category__slug'),
        brand_slug=F('brand__slug'),
        child_category_slug=F('child_category__slug'),
        product_slug=F('product__slug'),
    ).order_by('-viewed', 'deadline')
