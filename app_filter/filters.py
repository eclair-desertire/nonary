from django_filters import rest_framework as filters

from app_filter.models import CategoryFilter


class CategoryFilterFilter(filters.FilterSet):
    category = filters.CharFilter(field_name='category__slug')

    class Meta:
        model = CategoryFilter
        fields = ['category']
