from django.apps import apps
from django.db.models import F, Q, Case, When, Value, BooleanField, Prefetch, Count, Avg
from django.utils import timezone
from rest_framework.generics import get_object_or_404

from utils.aggregations import GetProductIsFavouriteAggregate
from utils.choices import StorehouseTypeChoices, CompilationTypeChoices
from utils.crud import get_object_queryset

Product = apps.get_model(app_label='shop', model_name='Product')
Property = apps.get_model(app_label='shop', model_name='Property')
ProductProperty = apps.get_model(app_label='shop', model_name='ProductProperty')
Brand = apps.get_model(app_label='shop', model_name='Brand')
Category = apps.get_model(app_label='shop', model_name='Category')
Subcategory = apps.get_model(app_label='shop', model_name='Subcategory')
ChildCategory = apps.get_model(app_label='shop', model_name='ChildCategory')
Delivery = apps.get_model(app_label='shop', model_name='Delivery')
ProductReview = apps.get_model(app_label='shop', model_name='ProductReview')
ReviewImage = apps.get_model(app_label='shop', model_name='ReviewImage')
ProductPrice = apps.get_model(app_label='shop', model_name='ProductPrice')
Compilation = apps.get_model(app_label='shop', model_name='Compilation')
Rest = apps.get_model(app_label='shop', model_name='Rest')
Currency=apps.get_model(app_label='shop',model_name='Currency')


def get_category_queryset(filter_lookup):
    return get_object_queryset(app_label='shop', model_name='Category', filter_lookup=filter_lookup)


def get_child_category_queryset(filter_lookup):
    return get_object_queryset(app_label='shop', model_name='ChildCategory', filter_lookup=filter_lookup)



def get_subcategory_queryset(filter_lookup):
    return get_object_queryset(
        app_label='shop', model_name='Subcategory', filter_lookup=filter_lookup
    ).select_related(
        'category'
    ).annotate(
        category_name=F('category__name'),
        category_slug=F('category__slug')
    )


def get_brand_queryset(filter_lookup):
    return get_object_queryset(app_label='shop', model_name='Brand', filter_lookup=filter_lookup).distinct()


def get_product_queryset(filter_lookup, user, is_list=False, order_by='-created_at', city_slug=None):
    user_id = 0
    if user.is_authenticated:
        user_id = user.id
    if not is_list:
        filter_lookup.update({
            'discount_price__gt': 0.0,
            'rest__gt': 0,
        })
    qs = Product.objects.select_related(
        'brand',
    ).annotate(
        rest=F(f'rests_dict__{city_slug}_{StorehouseTypeChoices.DISCOUNT}'),
        is_favourite=GetProductIsFavouriteAggregate('shop_product.id', user_id),
        price=F(f'prices_dict__{city_slug}_{StorehouseTypeChoices.BASIC}'),
        discount_price=F(f'prices_dict__{city_slug}_{StorehouseTypeChoices.DISCOUNT}'),
        popularity=Count('orders__id', distinct=True),
        rating=Avg('reviews__stars', filter=Q(reviews__is_active=True)),
        comments=Count('reviews__id', filter=Q(reviews__is_active=True), distinct=True),
        # popularity=GetProductPopularityAggregate('shop_product.id'),
        # rating=GetProductRatingAggregate('shop_product.id'),
        # comments=GetProductCommentsAggregate('shop_product.id'),
    ).filter(**filter_lookup, main_products__isnull=True)
    if is_list:
        qs = qs.prefetch_related(
            'categories', 'images',
            Prefetch(
                'similar_properties',
                queryset=Property.objects.order_by('position'),
                to_attr='similar_property_list'
            ),
            Prefetch(
                'properties',
                queryset=ProductProperty.objects.annotate(
                    is_multiple=Case(
                        When(
                            Q(product__similar_products__isnull=False) | Q(product__main_products__isnull=False),
                            then=Value(True, output_field=BooleanField())
                        ),
                        default=Value(False, output_field=BooleanField())
                    )
                ).filter(
                    property_value__value__isnull=False, is_active=True, property_value__property__is_active=True
                ).exclude(property_value__value='').annotate(
                    pr_position=F('property_value__property__position')
                ).order_by(
                    'pr_position'
                ).select_related(
                    'property_value',
                    'property_value__property',
                ).distinct(),
                to_attr='property_list'
            ),
            Prefetch(
                'similar_products',
                queryset=Product.objects.annotate(
                    rest=F(f'rests_dict__{city_slug}_{StorehouseTypeChoices.DISCOUNT}'),
                    price=F(f'prices_dict__{city_slug}_{StorehouseTypeChoices.BASIC}'),
                    discount_price=F(f'prices_dict__{city_slug}_{StorehouseTypeChoices.DISCOUNT}'),
                ).filter(
                    is_active=True,
                    discount_price__gt=0.0,
                    rest__gt=0
                ).prefetch_related(
                    Prefetch(
                        'properties',
                        queryset=ProductProperty.objects.filter(
                            property_value__isnull=False,
                            property_value__property__similar_products__isnull=False,
                            is_active=True, property_value__property__is_active=True,
                            property_value__value__isnull=False,
                        ).exclude(property_value__value='').annotate(
                            pr_position=F('property_value__property__position'),
                            is_multiple=Value(True, output_field=BooleanField()),
                        ).order_by(
                            'pr_position'
                        ).select_related(
                            'property_value',
                            'property_value__property',
                            'product',
                        ).prefetch_related(
                            'product__images'
                        ).distinct(),
                        to_attr='property_list'
                    )
                ),
                to_attr='similar_list'
            )
        ).select_related(
            'brand'
        )
    return qs.distinct().order_by(order_by)


EXCLUDE_KEYS = [
    'brand', 'category', 'ordering', 'page[number]', 'page[size]', 'search', 'stocks', 'level3', 'compilation',
    'city_slug', 'price_min', 'price_max',
]


def filter_by_property(queryset, query_params):
    filters = Q()
    for key, value in query_params.items():
        if key not in EXCLUDE_KEYS:
            filters = filters & (Q(properties__property_value__property__slug=key) &
                                 Q(properties__property_value__value__in=value.split(',')))
    queryset = queryset.filter(filters)
    return queryset.distinct()


def filter_by_compilation(queryset, compilation_id=None):
    if compilation_id:
        compilations = Compilation.objects.filter(id=compilation_id)
        compilation = get_object_or_404(compilations, id=compilation_id)
        if compilation.compilation_type == CompilationTypeChoices.IS_NEW:
            today = timezone.now().date() - timezone.timedelta(days=30)
            return queryset.filter(in_store_date__gte=today)
        elif compilation.compilation_type == CompilationTypeChoices.RECENTLY:
            today = timezone.now().date() - timezone.timedelta(days=2)
            return queryset.filter(seen_users__created_at__date__gte=today)
        product_ids = [_id for item in compilations.values_list('products__id') for _id in item]
        return queryset.filter(id__in=product_ids).distinct()
    return queryset


def get_delivery_queryset(city_slug):
    return Delivery.objects.filter(city__slug=city_slug, is_active=True).order_by('position').distinct()


def get_payment_queryset(filter_lookup):
    return get_object_queryset(
        app_label='shop', model_name='Payment', filter_lookup=filter_lookup
    )


def get_review_queryset(user, filter_lookup):
    if not user.is_authenticated:
        user = None
    return ProductReview.objects.filter(
        **filter_lookup
    ).select_related(
        'product', 'user'
    ).prefetch_related(
        Prefetch(
            'images',
            queryset=ReviewImage.objects.order_by(),
            to_attr='image_list'
        )
    ).alias(
        my_likes=Count('useful_users__id', filter=Q(useful_users__user=user), distinct=True)
    ).annotate(
        answered=Case(
            When(my_likes__gt=0, then=Value(True, output_field=BooleanField())),
            default=Value(False, output_field=BooleanField())
        ),
        likes=Count(
            'useful_users__id', filter=Q(useful_users__is_useful=True), distinct=True
        ) - Count(
            'useful_users__id', filter=Q(useful_users__is_useful=False), distinct=True
        )
    ).order_by('-created_at').distinct()


def get_similar_products(instance, user, city_slug=None):
    return get_product_queryset({'categories__in': instance.categories.all()}, user, city_slug=city_slug).exclude(
        id=instance.id)
    # return get_product_queryset({'same_products__id': instance.id}, user, city_slug=city_slug).exclude(id=instance.id)


def get_similar_by_brand(instance, user, city_slug=None):
    return get_product_queryset({'same_products__id': instance.id}, user, city_slug=city_slug).exclude(id=instance.id)


def get_buy_with_this(instance, user, city_slug=None):
    return get_product_queryset({'orders__order__items__product': instance}, user, city_slug=city_slug).exclude(id=instance.id)


def get_seen_products(user, city_slug=None):
    if user.is_authenticated:
        today = timezone.now().date() - timezone.timedelta(days=2)
        return get_product_queryset({'seen_users__user': user, 'seen_users__created_at__date__gte': today}, user,
                                    city_slug=city_slug)
    return Product.objects.none()


def get_compilation_queryset():
    return Compilation.objects.filter(is_active=True).order_by('position')
