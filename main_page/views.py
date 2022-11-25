from datetime import datetime

from drf_yasg.utils import swagger_auto_schema
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from main_page.serializers import StockListSerializer, StockSerializer, StorySerializer
from main_page.services.client.actions import set_viewed_story
from main_page.services.client.querysets import get_stock_queryset, get_story_queryset
from utils.choices import StoryTypeChoices
from utils.crud import get_object_by_lookup
from utils.manual_parameters import QUERY_CITY_SLUG
from utils.viewsets import CustomGenericViewSet


class StockViewSet(ListModelMixin, RetrieveModelMixin, CustomGenericViewSet):
    serializer_class = StockListSerializer
    permission_classes = (AllowAny, )

    def get_queryset(self):
        city_slug = self.request.query_params.get('city_slug', 'almaty')
        return get_stock_queryset(self.action, city_slug)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return StockSerializer
        return super(StockViewSet, self).get_serializer_class()

    @swagger_auto_schema(
        manual_parameters=[QUERY_CITY_SLUG]
    )
    def retrieve(self, request, *args, **kwargs):
        return super(StockViewSet, self).retrieve(request, *args, **kwargs)


class StoryViewSet(ListModelMixin, RetrieveModelMixin, CustomGenericViewSet):
    serializer_class = StorySerializer
    permission_classes = (AllowAny, )
    story_type = StoryTypeChoices.NORMAL

    def get_filter_lookup(self):
        today = datetime.now()
        return {'deadline__gt': today, 'is_active': True, 'story_type': self.story_type}

    def get_queryset(self):
        return get_story_queryset(self.request.user, self.get_filter_lookup())


class MiniBannerViewSet(StoryViewSet):
    story_type = StoryTypeChoices.MINI

    def get_queryset(self):
        return get_story_queryset(self.request.user, self.get_filter_lookup()).order_by('position')


class SetViewedStoryView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, pk):
        instance = get_object_by_lookup(app_label='main_page', model_name='UserViewedStory', filter_lookup={'pk': pk})
        set_viewed_story(instance, request.user)
        return Response({'message': 'OK'})
