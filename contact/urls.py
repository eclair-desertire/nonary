from django.urls import path
from rest_framework.routers import DefaultRouter

from contact.views import ContactListView, PublicOfferListView, AboutView, MagazineViewSet, RequisiteViewSet

router = DefaultRouter()

router.register('offer', PublicOfferListView, basename='offer-list')
router.register('requisites', RequisiteViewSet, basename='offer-list')
router.register('magazine', MagazineViewSet, basename='magazines')
router.register('', ContactListView, basename='contact-list')

urlpatterns = [
    path('about/', AboutView.as_view(), name='about')
] + router.urls
