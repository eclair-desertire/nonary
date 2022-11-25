from django.urls import path
from rest_framework.routers import DefaultRouter

from order.views import (
    AddBasketItemView, BasketDetailView, SetUserToBasket, CreateOrderView, OrderHistoryView, AddPromoToOrderView,
    FortePaymentTestView, CardRegistrationWebhook, OrderCreateNoBasketView, ChangeOrderDeliveryView,
    GetOrderPriceInfo, OrderInfoView, CopyOrderView, ClearBasket
)

router = DefaultRouter()
router.register('history', OrderHistoryView, basename='order-history')


urlpatterns = [
    path('add-to-basket/', AddBasketItemView.as_view(), name='add-to-basket'),
    path('add-promo/', AddPromoToOrderView.as_view(), name='add-promo-basket'),
    path('order-detail/<int:pk>/', OrderInfoView.as_view(), name='order-detail'),
    path('basket/<str:token>/', BasketDetailView.as_view(), name='basket-info'),
    path('assign-user/', SetUserToBasket.as_view(), name='assign-user'),
    path('create/<str:token>/', CreateOrderView.as_view(), name='create-order'),
    path('change-delivery/<str:token>/', ChangeOrderDeliveryView.as_view(), name='create-delivery'),
    path('get-prices/<str:token>/', GetOrderPriceInfo.as_view(), name='get-prices'),
    # path('create/', OrderCreateNoBasketView.as_view(), name='create-order-without-basket'),
    path('payment-<str:payment_status>/<str:order_id>/', CardRegistrationWebhook.as_view(), name='payment-webhook'),
    path('test-payment/', FortePaymentTestView.as_view()),
    path('copy/', CopyOrderView.as_view(), name='copy-order'),
    path('clear-basket/<str:token>/', ClearBasket.as_view(), name='clear-basket'),
] + router.urls
