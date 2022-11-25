from django.db.models import F, Prefetch, Count, Q, Case, When, Value, BooleanField

from utils.crud import get_object_queryset
from utils.utils import get_distance
from django.apps import apps


City = apps.get_model(app_label='location', model_name='City')
UserAddress = apps.get_model(app_label='location', model_name='UserAddress')


def get_address_queryset(filter_lookup: dict):
    qs = get_object_queryset(app_label='location', model_name='UserAddress', filter_lookup=filter_lookup)
    qs = qs.select_related('city')
    return qs


def get_post_queryset(filter_lookup: dict):
    return get_object_queryset(app_label='location', model_name='Post', filter_lookup=filter_lookup)


def filter_post_queryset(queryset, query_params, filter_lookup: dict):
    latitude = query_params.get('latitude')
    longitude = query_params.get('longitude')
    radius = query_params.get('radius')
    if latitude is not None and longitude is not None and radius is not None:
        return queryset.annotate(
            distance=get_distance(F('latitude'), F('longitude'), latitude, longitude),
        ).filter(
            distance__lt=radius, **filter_lookup
        ).order_by(
            'distance'
        )
    return queryset


def get_city_queryset(filter_lookup: dict):
    return get_object_queryset(app_label='location', model_name='City', filter_lookup=filter_lookup).alias(
        delivery_count=Count('deliveries__id', filter=Q(deliveries__is_active=True), distinct=True)
    ).annotate(
        has_delivery=Case(
            When(delivery_count__gt=0, then=Value(True, output_field=BooleanField())),
            default=Value(False, BooleanField()), output_field=BooleanField()
        )
    )


def filter_city_slug_post_queryset(queryset, city_slug):
    return queryset.filter(city__slug=city_slug)


def filter_category_by_city(queryset, city_slug):
    return queryset.filter(
        subcategories__child_categories__products__rests__storehouse__cities__slug=city_slug,
        subcategories__child_categories__products__rests__quantity__gt=0,
    ).distinct()


def filter_subcategory_by_city(queryset, city_slug):
    return queryset.filter(
        child_categories__products__rests__storehouse__cities__slug=city_slug,
        child_categories__products__rests__quantity__gt=0,
    ).distinct()


def filter_child_category_by_city(queryset, city_slug):
    return queryset.filter(
        products__rests__storehouse__cities__slug=city_slug,
        products__rests__quantity__gt=0,
    ).distinct()


def get_cities_with_addresses(user):
    user_address_qs = UserAddress.objects.none()
    if user.is_authenticated:
        user_address_qs = UserAddress.objects.filter(user=user, is_active=True)
    return City.objects.filter(is_active=True).prefetch_related(
        Prefetch(
            'addresses',
            queryset=user_address_qs,
            to_attr='address_list'
        )
    )
