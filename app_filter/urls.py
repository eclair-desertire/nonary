from django.urls import path
from rest_framework.routers import DefaultRouter
from app_filter.views import FilterListView, ValuesListView

router = DefaultRouter()

router.register('', FilterListView, basename='filters')

urlpatterns = [
    path('values/<str:property_slug>/', ValuesListView.as_view(), name='properties-values')
] + router.urls
