from django.urls import path
from rest_framework.routers import DefaultRouter

from shop.views import (
    CategoryViewSet, SubcategoryViewSet, BrandViewSet, ProductListView, FavouriteView, DeliveryListView,
    ProductSlugView, ProductExternalView, ReviewListView, CreateReviewView, CreateUsefulReviewView, TopBrandViewSet,
    ProductListFilterCountView, ProductSimilarListView, ChildCategoryViewSet, PaymentListView,
    ProductSimilarByBrandListView, ProductBuyWithListView, ProductSeenListView, CompilationListView
)

router = DefaultRouter()

router.register('categories', CategoryViewSet, basename='categories')
router.register('subcategories', SubcategoryViewSet, basename='subcategories')
router.register('child-categories', ChildCategoryViewSet, basename='child-categories')
router.register('top-brands', TopBrandViewSet, basename='brands')
router.register('brands', BrandViewSet, basename='brands')
router.register('goods-slug', ProductSlugView, basename='goods-slug')
router.register('goods-external-id', ProductExternalView, basename='goods-external-id')
router.register('reviews-create', CreateReviewView, basename='create-reviews')
router.register('reviews-useful', CreateUsefulReviewView, basename='reviews-useful')
router.register('reviews', ReviewListView, basename='reviews')
router.register('goods-count-filter', ProductListFilterCountView, basename='goods-count-filter')
router.register('similar-goods', ProductSimilarListView, basename='similar-goods')
router.register('last-seen-goods', ProductSeenListView, basename='last-seen-goods')
router.register('similar-brand-goods', ProductSimilarByBrandListView, basename='similar-brand-goods')
router.register('buy-with-goods', ProductBuyWithListView, basename='buy-with-goods')
router.register('goods', ProductListView, basename='goods')
router.register('payment-types', PaymentListView, basename='payment-types')
router.register('compilations', CompilationListView, basename='compilations')

urlpatterns = [
    path('favourite/', FavouriteView.as_view(), name='set-favourite'),
    path('deliveries/', DeliveryListView.as_view(), name='delivery-list'),
] + router.urls
