import json

from django.conf import settings
from django.db.models import Case, When, Value
from django.http import Http404
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from django.utils.encoding import force_str

from auth_user.filters import QuestionFilter
from auth_user.serializers import UserAuthSerializer, ProfileSerializer, UpdateUserCitySerializer, \
    UpdateUserEmailSerializer, ChangeEmailTokenSerializer, LoginSerializer, ProfileWithTokenSerializer, \
    ProfileEditSerializer, QuestionListSerializer, UsefulQuestionSerializer, FavouriteCountSerializer, \
    QuestionCategoryListSerializer, CardRegistrationURLSerializer, UserCardListSerializer, ChooseCardSerializer, \
    ChangeEmailCodeSerializer
from auth_user.services.client.cards import register_card
from auth_user.services.client.profile import update_current_user, request_email_change, change_email, \
    change_email_from_token, logout, request_change_phone, delete_account, change_email_from_code
from auth_user.services.client.queryset import get_question_queryset, get_useful_queryset, get_favourite_products, \
    get_favourite_count, get_question_category_queryset, clear_favourites, get_last_order
from auth_user.services.client.question import create_useful_question
from auth_user.services.client.user_auth import auth, verify_code
from auth_user.services.common import create_user_card_token, UserCard, delete_user_card_token
from order.serializers import LastOrderSerializer
from order.services.client.orders import get_order_history
from shop.serializers import ProductListSerializer, ProductCountSerializer
from utils.custom_logging import save_info
from utils.manual_parameters import QUERY_CITY_SLUG
from utils.querysets import get_user_queryset
from utils.viewsets import CustomGenericViewSet


class AuthView(CreateModelMixin, CustomGenericViewSet):
    serializer_class = UserAuthSerializer
    permission_classes = (AllowAny, )
    queryset = get_user_queryset({})

    @swagger_auto_schema(
        responses={200: ProfileWithTokenSerializer()}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token, user = auth(serializer.validated_data)
        return Response({
            'token': token,
            'user': ProfileSerializer(user, context=self.get_serializer_context()).data
        })


class VerifyPhoneNumberView(AuthView):
    serializer_class = LoginSerializer

    @swagger_auto_schema(
        responses={200: ProfileWithTokenSerializer()}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token, user = verify_code(serializer.validated_data)
        return Response({
            'token': token.key,
            'user': ProfileSerializer(user, context=self.get_serializer_context()).data
        })


class ProfileView(APIView):
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        responses={200: ProfileSerializer()}
    )
    def get(self, request):
        return Response(
            ProfileSerializer(request.user, context={'request': request}).data
        )

    def delete(self, request):
        delete_account(request.user, just_inactive=settings.JUST_INACTIVE)
        return Response(status=HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        request_body=ProfileEditSerializer(),
        responses={200: ProfileSerializer()}
    )
    def put(self, request):
        serializer = ProfileEditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = update_current_user(request.user, serializer.validated_data)
        return Response(
            ProfileSerializer(instance, context={'request': request}).data
        )


class UpdateCityView(APIView):
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        request_body=UpdateUserCitySerializer(),
        responses={200: ProfileSerializer()}
    )
    def put(self, request):
        serializer = UpdateUserCitySerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(
            ProfileSerializer(instance, context={'request': request}).data
        )


class ChangeEmailView(APIView):
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        request_body=UpdateUserEmailSerializer(),
        responses={200: ProfileSerializer()}
    )
    def put(self, request):
        serializer = UpdateUserEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if settings.IS_VERIFY_EMAIL:
            instance = request_email_change(request, request.user, serializer.validated_data)
        else:
            instance = change_email(request.user, serializer.validated_data)
        return Response(
            ProfileSerializer(instance, context={'request': request}).data
        )


class VerifyEmail(APIView):
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        request_body=ChangeEmailTokenSerializer(),
        responses={200: ProfileSerializer()}
    )
    def post(self, request):
        serializer = ChangeEmailTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = change_email_from_token(serializer.validated_data)
        return Response(
            ProfileSerializer(instance, context={'request': request}).data
        )


class VerifyEmailWithCode(APIView):
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        request_body=ChangeEmailCodeSerializer(),
        responses={200: ProfileSerializer()}
    )
    def post(self, request):
        serializer = ChangeEmailCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = change_email_from_code(request.user, serializer.validated_data)
        return Response(
            ProfileSerializer(instance, context={'request': request}).data
        )


class LogoutView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        logout(request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePhoneNumberView(APIView):
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        request_body=UserAuthSerializer(),
        responses={200: ProfileWithTokenSerializer()}
    )
    def post(self, request):
        serializer = UserAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token, instance = request_change_phone(request.user, serializer.validated_data)
        return Response({
            'token': token,
            'user': ProfileSerializer(instance, context={'request': request}).data
        })


class QuestionListView(ListModelMixin, CustomGenericViewSet):
    serializer_class = QuestionListSerializer
    permission_classes = (AllowAny, )
    filter_backends = (SearchFilter, DjangoFilterBackend)
    search_fields = ('question', )
    filterset_class = QuestionFilter

    def get_queryset(self):
        return get_question_queryset({'is_active': True}, user=self.request.user)


class QuestionCategoryListView(ListModelMixin, CustomGenericViewSet):
    serializer_class = QuestionCategoryListSerializer
    permission_classes = (AllowAny, )
    pagination_class = None

    def get_queryset(self):
        return get_question_category_queryset({'is_active': True})


class UsefulQuestionView(CreateModelMixin, CustomGenericViewSet):
    serializer_class = UsefulQuestionSerializer
    permission_classes = (IsAuthenticated, )
    queryset = get_useful_queryset({})

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        create_useful_question(request.user, serializer.validated_data)
        return Response(serializer.initial_data)


class FavouriteProductList(ListModelMixin, GenericViewSet):
    serializer_class = ProductListSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        city_slug = None
        if 'city_slug' in self.request.query_params:
            city_slug = self.request.query_params.get('city_slug')
        return get_favourite_products(self.request.user, city_slug=city_slug)

    @swagger_auto_schema(
        manual_parameters=[QUERY_CITY_SLUG]
    )
    def list(self, request, *args, **kwargs):
        return super(FavouriteProductList, self).list(request, *args, **kwargs)


class GetFavouriteCount(APIView):
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        responses={200: FavouriteCountSerializer()}
    )
    def get(self, request):
        return Response(
            {'favourite_count': get_favourite_count(request.user)}
        )


class GetCardRegistrationURLView(APIView):
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        responses={200: CardRegistrationURLSerializer()}
    )
    def get(self, request):
        url = register_card(request)
        return Response({
            'url': url
        })


class ApproveDeclineCardRegistrationView(APIView):

    def post(self, request, status_type, user_id):
        text_msg = 'Error'
        save_info(json.dumps(dict(request.data)))
        if status_type == 'success':
            user_id = force_str(urlsafe_base64_decode(user_id))
            card_token = request.data.get('cardUID')
            pan = request.data.get('maskedPAN')
            cardholder_name = request.data.get('cardHolderName')
            brand = request.data.get('brand')
            initial_transaction_id = request.data.get('initialTransactionId')
            initial_external_transaction_id = request.data.get('initialExternalTransactionId')
            initial_rrn = request.data.get('initialRRN')
            create_user_card_token(user_id, pan, brand, card_token)
            text_msg = 'Карта успешно добавлена!'
        html = render_to_string(
            'tokenization.html',
            {'message': text_msg}
        )
        return render(
            request,
            'tokenization.html',
            {'message': text_msg}
        )

    def get(self, request, status_type, user_id):
        save_info(json.dumps(dict(request.data)))
        save_info(json.dumps(request.query_params.dict()))
        text_msg = 'Error'
        if status_type == 'success':
            text_msg = 'Карта успешно добавлена!'
        html = render_to_string(
            'tokenization.html',
            {'message': text_msg}
        )
        return render(
            request,
            'tokenization.html',
            {'message': text_msg}
        )


class UserCardListView(ListModelMixin, GenericViewSet):
    serializer_class = UserCardListSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return UserCard.objects.filter(user=self.request.user).annotate(
                is_selected=Case(
                    When(users__isnull=False, then=Value(True)),
                    default=Value(False)
                )
            )
        return UserCard.objects.none()


class ChoseCardView(APIView):
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        request_body=ChooseCardSerializer()
    )
    def post(self, request):
        user = request.user
        serializer = ChooseCardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if user == serializer.validated_data.get('card').user:
            user.selected_card = serializer.validated_data.get('card')
            user.save()
            return Response({'message': 'OK'})
        return Response({'message': 'Not fund'}, status=404)


@csrf_exempt
def debug_tokenization(request, status_type, user_id):
    text_msg = 'Error'
    print(request.POST)
    if status_type == 'success':
        # user_id = force_str(urlsafe_base64_decode(user_id))
        # card_token = request.data.get('cardUID')
        # pan = request.data.get('maskedPAN')
        # cardholder_name = request.data.get('cardHolderName')
        # brand = request.data.get('brand')
        # initial_transaction_id = request.data.get('initialTransactionId')
        # initial_external_transaction_id = request.data.get('initialExternalTransactionId')
        # initial_rrn = request.data.get('initialRRN')
        # create_user_card_token(user_id, pan, brand, card_token)
        text_msg = 'Карта успешно добавлена!'
    html = render_to_string(
        'tokenization.html',
        {'message': text_msg}
    )
    return render(
        request,
        'tokenization.html',
        {'message': text_msg}
    )


class ClearFavouritesView(APIView):

    def delete(self, request):
        clear_favourites(request.user)
        return Response(status=HTTP_204_NO_CONTENT)


class GetLastOrderStatusView(APIView):
    """
    Для получения последнего заказа, в профиле "мои заказы: доставка и ПВЗ" (тут нельзя отправлять city_slug)
    Или на главной под городом! (для этого нужно отправить city_slug)
    """
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        manual_parameters=[QUERY_CITY_SLUG],
        responses={200: LastOrderSerializer(), 404: openapi.Response(description='Объект не найден', examples={
            "application/json": {
                "detail": "Страница не найдена."
            }
        })}
    )
    def get(self, request):
        city_slug = request.query_params.get('city_slug', None)
        instance = get_last_order(request.user, city_slug=city_slug)
        if instance:
            return Response(LastOrderSerializer(instance, context={'request': request}).data)
        raise Http404


class DeleteUserCardTokenView(APIView):
    permission_classes = (IsAuthenticated, )

    def delete(self, request, card_id):
        instance = get_object_or_404(UserCard, pk=card_id, user=request.user)
        delete_user_card_token(instance)
        return Response(status=HTTP_204_NO_CONTENT)


class GetOrdersCountView(APIView):
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        responses={
            200: ProductCountSerializer()
        }
    )
    def get(self, request):
        orders = get_order_history(self.request.user)
        return Response({'count': orders.count()})
