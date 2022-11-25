from django.urls import path
from rest_framework.routers import DefaultRouter
from main_page.views import (
    StockViewSet, StoryViewSet, SetViewedStoryView, MiniBannerViewSet
)
router = DefaultRouter()

router.register('stocks', StockViewSet, basename='stocks')
router.register('stories', StoryViewSet, basename='stories')
router.register('mini-banners', MiniBannerViewSet, basename='mini-banners')


urlpatterns = [
    path('story/<int:pk>/', SetViewedStoryView.as_view(), name='set-story-viewed')
] + router.urls
