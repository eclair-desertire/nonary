from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework.mixins import ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from app_filter.filters import CategoryFilterFilter
from app_filter.serializers import FilterListSerializer
from app_filter.models import CategoryFilter
from app_filter.services.client.values import get_values
from utils.manual_parameters import QUERY_CATEGORY_SLUG


class FilterListView(ListModelMixin, GenericViewSet):
    serializer_class = FilterListSerializer
    queryset = CategoryFilter.objects.filter(is_active=True).select_related('property')
    permission_classes = (AllowAny, )
    pagination_class = None
    filter_backends = (DjangoFilterBackend, )
    filterset_class = CategoryFilterFilter


class ValuesListView(APIView):
    permission_classes = (AllowAny, )

    @swagger_auto_schema(
        manual_parameters=[QUERY_CATEGORY_SLUG]
    )
    def get(self, request, property_slug):
        category_slug = request.query_params.dict().get('category')
        return Response(get_values(property_slug, category_slug=category_slug))
