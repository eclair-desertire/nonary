from django_filters import rest_framework as filters

from location.models import Post, UserAddress


class PostObjectsFilter(filters.FilterSet):
    city_slug = filters.CharFilter(field_name='city__slug')

    class Meta:
        model = Post
        fields = ['city_slug']


class AddressFilter(filters.FilterSet):
    city_slug = filters.CharFilter(field_name='city__slug')

    class Meta:
        model = UserAddress
        fields = ['city_slug']
