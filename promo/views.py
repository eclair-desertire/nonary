from django.apps import apps
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from promo.serializers import SelectedPromoSerializer, AddPromoSerializer, SelectPromoSerializer, PromoSerializer
from promo.services.client.crud import get_selected_promo, add_promo, select_promo, get_promo_list

UserPromo = apps.get_model('promo', 'UserSelectedPromo')


class MyPromoListView(ListModelMixin, GenericViewSet):
    serializer_class = SelectedPromoSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return get_selected_promo(self.request.user)


class AddPromoView(CreateModelMixin, GenericViewSet):
    serializer_class = AddPromoSerializer
    permission_classes = (IsAuthenticated, )
    queryset = UserPromo.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        add_promo(serializer.validated_data, request.user)
        return Response({'message': 'created'})


class SelectPromoView(CreateModelMixin, GenericViewSet):
    serializer_class = SelectPromoSerializer
    permission_classes = (IsAuthenticated, )
    queryset = UserPromo.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        select_promo(serializer.validated_data.get('promo'))
        return Response({'message': 'selected'})


class PromoRetrieveView(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = PromoSerializer
    lookup_field = 'name'

    def get_queryset(self):
        is_auto = self.action == 'list'
        return get_promo_list(self.request.user, is_auto=is_auto)
