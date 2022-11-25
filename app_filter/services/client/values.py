from django.db.models import F

from shop.models import ProductProperty


def get_values(slug, category_slug=None):
    extra_lookup = {}
    if category_slug:
        extra_lookup.update({
            'product__categories__category__slug': category_slug
        })
    return list(ProductProperty.objects.filter(
        property_value__property__slug=slug, is_active=True, **extra_lookup
    ).annotate(
        value=F('property_value__value')
    ).order_by('value').values_list('value', flat=True).distinct())
