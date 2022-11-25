from django.apps import apps
from django.db.models import Case, When, Value, BooleanField, Avg, Q, F, Count, Subquery, OuterRef

from utils.choices import StorehouseTypeChoices, OrderStatusChoices
from utils.crud import get_object_queryset
from utils.subqueries import get_product_subqueries

ProductPrice = apps.get_model(app_label='shop', model_name='ProductPrice')
Rest = apps.get_model(app_label='shop', model_name='Rest')
Order = apps.get_model(app_label='order', model_name='Order')


def get_question_queryset(filter_lookup: dict, user=None):
    qs = get_object_queryset(app_label='auth_user', model_name='Question', filter_lookup=filter_lookup)
    if user is not None:
        qs = qs.alias(answer_count=Count('users__id', filter=Q(users__user=user))).annotate(
            answered=Case(
                When(answer_count__gt=0, then=Value(True, output_field=BooleanField())),
                default=Value(False, output_field=BooleanField())
            )
        )
    else:
        qs = qs.annotate(answered=Value(False, output_field=BooleanField()))
    return qs.distinct()


def get_useful_queryset(filter_lookup: dict):
    return get_object_queryset(app_label='auth_user', model_name='UsefulQuestion',
                               filter_lookup=filter_lookup).distinct()


def get_question_category_queryset(filter_lookup: dict):
    return get_object_queryset(app_label='auth_user', model_name='QuestionCategory',
                               filter_lookup=filter_lookup).distinct()


def get_favourite_products(user, city_slug=None):
    # discount_price_subquery, product_rest_subquery, price_subquery = get_product_subqueries(city_slug=city_slug)
    return get_object_queryset(
        app_label='shop', model_name='Product',
        filter_lookup={'favourites__user': user}
    ).annotate(
        rest=F(f'rests_dict__{city_slug}_{StorehouseTypeChoices.DISCOUNT}'),
        is_favourite=Value(True, output_field=BooleanField()),
        rating=Avg('reviews__stars', filter=Q(reviews__is_active=True)),
        price=F(f'prices_dict__{city_slug}_{StorehouseTypeChoices.BASIC}'),
        discount_price=F(f'prices_dict__{city_slug}_{StorehouseTypeChoices.DISCOUNT}'),
        popularity=Count('orders__id', distinct=True),
        comments=Count('reviews__id', filter=Q(reviews__is_active=True), distinct=True),
    ).select_related('brand').distinct()


def get_favourite_count(user):
    return get_object_queryset(app_label='auth_user', model_name='FavouriteProduct',
                               filter_lookup={'user': user}).distinct().count()


def clear_favourites(user):
    get_object_queryset(app_label='auth_user', model_name='FavouriteProduct',
                        filter_lookup={'user': user}).delete()


def get_last_order(user, city_slug=None):
    additional_filter = Q()
    if city_slug:
        additional_filter = (
                Q(address__address__city__slug=city_slug) | Q(pickup__pickup__city__slug=city_slug) |
                Q(post__post__city__slug=city_slug)
        )
    orders = Order.objects.filter(additional_filter, user=user, is_basket=False).exclude(
        status__in=[OrderStatusChoices.DELIVERED, OrderStatusChoices.COMPLETED, OrderStatusChoices.CANCELED]
    ).select_related(
        'delivery', 'address', 'address__address', 'pickup', 'pickup__pickup', 'post', 'post__post',
    ).annotate(delivery_type=F('delivery__delivery_type')).order_by('-created_at').distinct()
    return orders.first()
