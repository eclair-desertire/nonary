from django.urls import path
from rest_framework.routers import DefaultRouter

from location.views import (
    UserAddressViewSet, PostReadOnlyViewSet, PickupPointReadOnlyViewSet, CityListView, SelectCityView, PostListView,
    PickupPointListView, CityListWithAddressView, GetYandexMapResult
)

router = DefaultRouter()

router.register('user-addresses', UserAddressViewSet, basename='user-addresses')
router.register('order-posts', PostListView, basename='order-posts')
router.register('posts', PostReadOnlyViewSet, basename='posts')
router.register('cities-with-addresses', CityListWithAddressView, basename='cities-with-addresses')
router.register('cities', CityListView, basename='cities')
router.register('order-pickup-points', PickupPointListView, basename='order-pickup-points')
router.register('pickup-points', PickupPointReadOnlyViewSet, basename='pickup-points')

urlpatterns = [
    path('select-city/', SelectCityView.as_view(), name='select-city'),
    path('yandex-search/', GetYandexMapResult.as_view(), name='select')

] + router.urls
