from rest_framework.routers import DefaultRouter
from promo.views import (
    SelectPromoView, MyPromoListView, AddPromoView, PromoRetrieveView
)

router = DefaultRouter()

router.register('my-promo-list', MyPromoListView, basename='my-promo-list')
router.register('add-promo', AddPromoView, basename='add-promo')
# router.register('select-promo', SelectPromoView, basename='select-promo')
router.register('', PromoRetrieveView, basename='promo-view')

urlpatterns = router.urls
