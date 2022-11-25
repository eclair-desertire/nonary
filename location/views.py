from django.apps import apps
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework.filters import SearchFilter
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_200_OK, HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from auth_user.serializers import CitySerializer
from location.filters import PostObjectsFilter
from location.serializers import AddressListSerializer, AddressCreateUpdateSerializer, PostSerializer, \
    PostFilterSerializer, SelectCitySerializer, PostQuerySerializer, CityWithAddressSerializer, YandexResponseSerializer
from location.services.client.action import select_city
from location.services.client.querysets import get_address_queryset, get_post_queryset, filter_post_queryset, \
    get_city_queryset, filter_city_slug_post_queryset, get_cities_with_addresses
from location.services.client.yandex_map import search_by_coordinates
from utils.choices import ObjectTypeChoices
from utils.crud import create_object, update_object, change_is_active
from utils.manual_parameters import QUERY_LATITUDE, QUERY_LONGITUDE, QUERY_RADIUS, QUERY_CITY_SLUG, QUERY_GEOCODE, \
    QUERY_FROM_MAP
from utils.viewsets import CustomGenericViewSet


class UserAddressViewSet(ModelViewSet):
    serializer_class = AddressListSerializer
    permission_classes = (IsAuthenticated, )
    filter_backends = (SearchFilter,)
    search_fields = ('title', 'address', 'office', 'city__name')
    # filterset__class = AddressFilter

    def get_serializer_class(self):
        if self.action not in ('list', 'retrieve'):
            return AddressCreateUpdateSerializer
        return super(UserAddressViewSet, self).get_serializer_class()

    def get_queryset(self):
        if self.request.user.is_authenticated:
            filter_lookup = {
                'user': self.request.user
            }
            return get_address_queryset(filter_lookup)
        return apps.get_model(app_label='location', model_name='UserAddress').objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = {'user': request.user, **serializer.validated_data}
        instance = create_object(app_label='location', model_name='UserAddress',
                                 validated_data=validated_data)
        return Response(
            self.get_serializer(instance).data, status=HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = update_object(instance, validated_data=serializer.validated_data)
        return Response(
            self.get_serializer(instance).data, status=HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        change_is_active(instance)
        return Response(status=HTTP_204_NO_CONTENT)


class PostReadOnlyViewSet(ListModelMixin, RetrieveModelMixin, CustomGenericViewSet):
    serializer_class = PostSerializer
    permission_classes = (AllowAny, )
    pagination_class = None
    queryset = get_post_queryset({'object_type': ObjectTypeChoices.POST, 'is_active': True})
    filter_backends = (SearchFilter, DjangoFilterBackend, )
    search_fields = ('name', 'address',)
    filterset_class = PostObjectsFilter
    
    def filter_queryset(self, queryset):
        queryset = super(PostReadOnlyViewSet, self).filter_queryset(queryset)
        query_serializer = PostFilterSerializer(data=self.request.query_params)
        query_serializer.is_valid(raise_exception=True)
        return filter_post_queryset(queryset, query_serializer.validated_data, {})

    @swagger_auto_schema(
        manual_parameters=[QUERY_LATITUDE, QUERY_LONGITUDE, QUERY_RADIUS, QUERY_CITY_SLUG]
    )
    def list(self, request, *args, **kwargs):
        """
        Used for search in map
        """
        return super(PostReadOnlyViewSet, self).list(request, *args, **kwargs)


class PickupPointReadOnlyViewSet(PostReadOnlyViewSet):
    queryset = get_post_queryset({'object_type': ObjectTypeChoices.PICKUP, 'is_active': True})


class CityListView(ListModelMixin, GenericViewSet):
    serializer_class = CitySerializer
    permission_classes = (AllowAny, )
    pagination_class = None
    queryset = get_city_queryset({'is_active': True})
    filter_backends = (SearchFilter, )
    search_fields = ('name', )


class CityListWithAddressView(ListModelMixin, GenericViewSet):
    serializer_class = CityWithAddressSerializer
    permission_classes = (AllowAny, )
    pagination_class = None

    def get_queryset(self):
        return get_cities_with_addresses(self.request.user)


class SelectCityView(APIView):
    permission_classes = (AllowAny, )

    @swagger_auto_schema(
        request_body=SelectCitySerializer()
    )
    def post(self, request):
        serializer = SelectCitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        city = select_city(request.user, serializer.validated_data.get('city'))
        return Response(CitySerializer(city).data)


class PostListView(ListModelMixin, GenericViewSet):
    serializer_class = PostSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    queryset = get_post_queryset({'object_type': ObjectTypeChoices.POST, 'is_active': True})
    filter_backends = (SearchFilter,)
    search_fields = ('name', 'address',)

    def filter_queryset(self, queryset):
        if self.request.user.is_authenticated:
            city_slug = self.request.user.city.slug
        else:
            query_serializer = PostQuerySerializer(data=self.request.query_params)
            query_serializer.is_valid(raise_exception=True)
            city_slug = query_serializer.validated_data.get('city_slug')
        return filter_city_slug_post_queryset(queryset, city_slug)

    @swagger_auto_schema(
        manual_parameters=[QUERY_CITY_SLUG]
    )
    def list(self, request, *args, **kwargs):
        """
        Used for search in order request
        """
        return super(PostListView, self).list(request, *args, **kwargs)


class PickupPointListView(PostListView):
    queryset = get_post_queryset({'object_type': ObjectTypeChoices.PICKUP, 'is_active': True})


class GetYandexMapResult(APIView):

    @swagger_auto_schema(
        manual_parameters=[QUERY_GEOCODE, QUERY_CITY_SLUG, QUERY_FROM_MAP],
        responses={200: YandexResponseSerializer()}
    )
    def get(self, request):
        response, status_code = search_by_coordinates(request.query_params.get('geocode'),
                                                      city_slug=request.query_params.get('city_slug'),
                                                      from_map=request.query_params.get('from_map') == 'true')
        if status_code != 200:
            return Response({'message': 'Not found'}, status=status_code)
        return Response(response, status=status_code)
