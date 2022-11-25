from django.db.models import OuterRef
from django.apps import apps
from utils.choices import StorehouseTypeChoices


ProductPrice = apps.get_model(app_label='shop', model_name='ProductPrice')
Rest = apps.get_model(app_label='shop', model_name='Rest')


def get_product_subqueries(city_slug):
    storehouse_filter = {}
    if city_slug:
        storehouse_filter = {'storehouse__cities__slug': city_slug}
    discount_price_subquery = ProductPrice.objects.filter(
        product_id=OuterRef('pk'),
        storehouse__storehouse_type=StorehouseTypeChoices.DISCOUNT,
        **storehouse_filter
    ).values('price')[:1]
    product_rest_subquery = Rest.objects.filter(
        product_id=OuterRef('pk'),
        storehouse__storehouse_type=StorehouseTypeChoices.DISCOUNT,
        **storehouse_filter
    ).values('quantity')[:1]
    price_subquery = ProductPrice.objects.filter(
        product_id=OuterRef('pk'),
        storehouse__storehouse_type=StorehouseTypeChoices.BASIC,
        **storehouse_filter
    ).values('price')[:1]

    return discount_price_subquery, product_rest_subquery, price_subquery
