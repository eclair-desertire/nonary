from django.urls import path
from rest_framework.routers import DefaultRouter

from auth_user.views import (
    AuthView, ProfileView, UpdateCityView, ChangeEmailView, VerifyEmail, LogoutView, VerifyPhoneNumberView,
    ChangePhoneNumberView, QuestionListView, UsefulQuestionView, FavouriteProductList, GetFavouriteCount,
    QuestionCategoryListView, GetCardRegistrationURLView, ApproveDeclineCardRegistrationView, UserCardListView,
    ChoseCardView, ClearFavouritesView, GetLastOrderStatusView, GetOrdersCountView,
    debug_tokenization, VerifyEmailWithCode, DeleteUserCardTokenView
)

router = DefaultRouter()

router.register('favourite-products', FavouriteProductList, basename='favourite-products')
router.register('auth', AuthView, basename='auth-view')
router.register('questions-categories', QuestionCategoryListView, basename='questions-categories')
router.register('questions', QuestionListView, basename='questions')
router.register('useful-questions', UsefulQuestionView, basename='useful-questions')
router.register('verify-code', VerifyPhoneNumberView, basename='verify-code')
router.register('my-cards', UserCardListView, basename='card-list')

urlpatterns = [
    path('favourite-count/', GetFavouriteCount.as_view(), name='favourite-count'),
    path('card-registration-url/', GetCardRegistrationURLView.as_view(), name='card-registration-url'),
    path('save-card-<str:status_type>/<str:user_id>/', ApproveDeclineCardRegistrationView.as_view(), name='card-url'),
    # path('save-card-<str:status_type>/<str:user_id>/', debug_tokenization, name='debug-tokenization'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('change-city/', UpdateCityView.as_view(), name='change-city'),
    path('change-email/', ChangeEmailView.as_view(), name='change-email'),
    path('change-phone-number/', ChangePhoneNumberView.as_view(), name='change-phone-number'),
    path('verify-email/', VerifyEmailWithCode.as_view(), name='verify-email'),
    # path('verify-email-by-link/', VerifyEmail.as_view(), name='verify-email'),
    path('chose-card/', ChoseCardView.as_view(), name='chose-card'),
    path('clear-favourites/', ClearFavouritesView.as_view(), name='clear-favourites'),
    path('last-order/', GetLastOrderStatusView.as_view(), name='last-order'),
    path('orders-count/', GetOrdersCountView.as_view(), name='orders-count'),
    path('delete-card/<int:card_id>/', DeleteUserCardTokenView.as_view(), name='delete-card'),
] + router.urls
