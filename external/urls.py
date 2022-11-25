from django.urls import path

from external.views import (
    WebHookCommerceMLView, ExportOrdersView
)

urlpatterns = [
    path('commerce-ml/', WebHookCommerceMLView.as_view(), name='webhook-commerce-ml'),
    path('orders/', ExportOrdersView.as_view(), name='export-orders'),
]
