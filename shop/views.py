from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from location.services.client.querysets import filter_category_by_city, filter_subcategory_by_city, \
    filter_child_category_by_city
from shop.filters import SubcategoryFilter, ProductFilter, ReviewFilter, ChildCategoryFilter, BrandFilter, \
    CompilationFilter
from shop.serializers import CategorySerializer, SubcategoryDetailSerializer, ProductListSerializer, \
    FavouriteProductSerializer, DeliveryListSerializer, DeliveryQuerySerializer, ProductDetailSerializer, \
    ProductDetailResponseSerializer, ReviewListSerializer, ReviewCreateSerializer, UsefulReviewSerializer, \
    ProductCountSerializer, SimilarProductQuerySerializer, ChildCategorySerializer, PaymentListSerializer, \
    CompilationSerializer
from shop.services.client.querysets import get_subcategory_queryset, get_category_queryset, get_brand_queryset, \
    get_product_queryset, filter_by_property, get_delivery_queryset, get_review_queryset, get_similar_products, \
    get_child_category_queryset, get_payment_queryset, get_similar_by_brand, get_buy_with_this, get_seen_products, \
    get_compilation_queryset, filter_by_compilation
from shop.services.client.user import set_unset_favourite, set_seen_product
from utils.crud import get_object_queryset
from utils.manual_parameters import QUERY_CITY_SLUG, QUERY_ORDERING, QUERY_PRODUCT_ID, QUERY_COMPILATION
from utils.viewsets import CustomGenericViewSet


class CategoryViewSet(ListModelMixin, RetrieveModelMixin, CustomGenericViewSet):
    queryset = get_category_queryset({})
    permission_classes = (AllowAny, )
    serializer_class = CategorySerializer
    lookup_field = 'slug'

    @swagger_auto_schema(
        manual_parameters=[QUERY_CITY_SLUG]
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if 'city_slug' in request.query_params:
            queryset = filter_category_by_city(queryset, request.query_params.get('city_slug'))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SubcategoryViewSet(ListModelMixin, RetrieveModelMixin, CustomGenericViewSet):
    queryset = get_subcategory_queryset({})
    permission_classes = (AllowAny, )
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = SubcategoryFilter
    search_fields = ('name', )
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SubcategoryDetailSerializer
        return super(SubcategoryViewSet, self).get_serializer_class()

    @swagger_auto_schema(
        manual_parameters=[QUERY_CITY_SLUG]
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if 'city_slug' in request.query_params:
            queryset = filter_subcategory_by_city(queryset, request.query_params.get('city_slug'))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ChildCategoryViewSet(ListModelMixin, GenericViewSet):
    queryset = get_child_category_queryset({})
    permission_classes = (AllowAny,)
    serializer_class = ChildCategorySerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_class = ChildCategoryFilter
    search_fields = ('name',)

    def get_serializer_class(self):
        return super(ChildCategoryViewSet, self).get_serializer_class()

    @swagger_auto_schema(
        manual_parameters=[QUERY_CITY_SLUG]
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        if 'city_slug' in request.query_params:
            queryset = filter_child_category_by_city(queryset, request.query_params.get('city_slug'))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class BrandViewSet(CategoryViewSet):
    queryset = get_brand_queryset({'is_active': True}).order_by('name')
    filter_backends = (DjangoFilterBackend, SearchFilter, )
    search_fields = ('name', )
    filterset_class = BrandFilter
    pagination_class = None


class TopBrandViewSet(CategoryViewSet):
    queryset = get_brand_queryset({'is_active': True, 'is_top': True}).order_by('name')
    pagination_class = None


class ProductListView(ListModelMixin, CustomGenericViewSet):
    """
    Filter by property! Key should be equal to slug from /api/filters/
    AND value should be from /api/filters/values/{property_slug}/
    """
    serializer_class = ProductListSerializer
    permission_classes = (AllowAny, )
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    search_fields = ('name', 'brand__name')
    ordering_fields = ('name', 'discount_price', 'created_at', 'popularity', 'rating')
    filterset_class = ProductFilter

    def get_queryset(self):
        city_slug = None
        if 'city_slug' in self.request.query_params:
            city_slug = self.request.query_params.get('city_slug')
        if not city_slug:
            cities = get_object_queryset('location', 'City', {'slug': 'almaty'})
            if cities.exists():
                city_slug = cities.first().slug
            else:
                cities = get_object_queryset('location', 'City', {})
                if cities.exists():
                    city_slug = cities.first().slug
        return get_product_queryset({'is_active': True}, self.request.user, city_slug=city_slug)

    @swagger_auto_schema(
        manual_parameters=[QUERY_ORDERING, QUERY_COMPILATION, QUERY_CITY_SLUG]
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = filter_by_property(queryset, request.query_params)
        compilation = request.query_params.get('compilation', [])
        if len(compilation) > 0:
            queryset = filter_by_compilation(queryset, compilation[0])
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ProductListFilterCountView(ProductListView):
    pagination_class = None

    @swagger_auto_schema(
        responses={200: ProductCountSerializer()},
        manual_parameters=[QUERY_CITY_SLUG]
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = filter_by_property(queryset, request.query_params)
        return Response({'count': queryset.count()})


class ProductSlugView(RetrieveModelMixin, CustomGenericViewSet):
    serializer_class = ProductDetailSerializer
    permission_classes = (AllowAny, )
    lookup_field = 'slug'

    def get_queryset(self):
        city_slug = None
        if 'city_slug' in self.request.query_params:
            city_slug = self.request.query_params.get('city_slug')
        return get_product_queryset({}, self.request.user, is_list=True, city_slug=city_slug)

    @swagger_auto_schema(
        responses={200: ProductDetailResponseSerializer()},
        manual_parameters=[QUERY_CITY_SLUG]
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        set_seen_product(instance, request.user)
        return Response(serializer.data)


class ProductSimilarListView(ListModelMixin, GenericViewSet):
    serializer_class = ProductListSerializer
    permission_classes = (AllowAny, )

    @swagger_auto_schema(
        manual_parameters=[QUERY_PRODUCT_ID, QUERY_CITY_SLUG]
    )
    def list(self, request, *args, **kwargs):
        return super(ProductSimilarListView, self).list(request, *args, **kwargs)

    def get_object(self):
        serializer = SimilarProductQuerySerializer(data=self.request.query_params)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data.get('product')

    def get_queryset(self):
        city_slug = None
        if 'city_slug' in self.request.query_params:
            city_slug = self.request.query_params.get('city_slug')
        return get_similar_products(self.get_object(), self.request.user, city_slug=city_slug).distinct()


class ProductSimilarByBrandListView(ProductSimilarListView):

    def get_queryset(self):
        city_slug = None
        if 'city_slug' in self.request.query_params:
            city_slug = self.request.query_params.get('city_slug')
        return get_similar_by_brand(self.get_object(), self.request.user, city_slug=city_slug).distinct()


class ProductBuyWithListView(ProductSimilarListView):

    def get_queryset(self):
        city_slug = None
        if 'city_slug' in self.request.query_params:
            city_slug = self.request.query_params.get('city_slug')
        return get_buy_with_this(self.get_object(), self.request.user, city_slug=city_slug).distinct()


class ProductSeenListView(ListModelMixin, GenericViewSet):
    serializer_class = ProductListSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        city_slug = None
        if 'city_slug' in self.request.query_params:
            city_slug = self.request.query_params.get('city_slug')
        return get_seen_products(self.request.user, city_slug=city_slug).distinct()
    
    @swagger_auto_schema(
        manual_parameters=[QUERY_CITY_SLUG]
    )
    def list(self, request, *args, **kwargs):
        return super(ProductSeenListView, self).list(request, *args, **kwargs)


class ProductExternalView(ProductSlugView):
    lookup_field = 'external_id'


class FavouriteView(APIView):
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        request_body=FavouriteProductSerializer()
    )
    def post(self, request):
        serializer = FavouriteProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        set_unset_favourite(serializer.validated_data.get('product'), request.user)
        return Response({'message': 'OK'})


class PaymentListView(ListModelMixin, GenericViewSet):
    serializer_class = PaymentListSerializer
    pagination_class = None
    queryset = get_payment_queryset({'is_active': True})


class DeliveryListView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        responses={200: DeliveryListSerializer(many=True)},
        manual_parameters=[QUERY_CITY_SLUG]
    )
    def get(self, request):
        query_serializer = DeliveryQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)
        city_slug = query_serializer.validated_data.get('city_slug')
        serializer = DeliveryListSerializer(get_delivery_queryset(city_slug), many=True)
        return Response(serializer.data)


class ReviewListView(ListModelMixin, GenericViewSet):
    serializer_class = ReviewListSerializer
    permission_classes = (AllowAny, )
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = ReviewFilter
    ordering_fields = ['created_at', 'stars', 'likes']

    def get_queryset(self):
        return get_review_queryset(self.request.user, {})


class CreateReviewView(CreateModelMixin, GenericViewSet):
    serializer_class = ReviewCreateSerializer
    permission_classes = (IsAuthenticated, )
    parser_classes = (MultiPartParser, )

    def get_queryset(self):
        return get_review_queryset(self.request.user, {})

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CreateUsefulReviewView(CreateModelMixin, GenericViewSet):
    serializer_class = UsefulReviewSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return get_object_queryset(app_label='shop', model_name='ReviewUseful', filter_lookup={})

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CompilationListView(ListModelMixin, GenericViewSet):
    serializer_class = CompilationSerializer
    permission_classes = (AllowAny, )
    queryset = get_compilation_queryset()
    pagination_class = None
    filter_backends = (DjangoFilterBackend, SearchFilter, )
    search_fields = ('name', )
    filterset_class = CompilationFilter
