from drf_yasg.utils import swagger_auto_schema
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from contact.serializers import ContactListSerializer, PublicOfferListSerializer, AboutSerializer, MagazineSerializer, \
    RequisiteSerializer
from contact.services.client.querysets import get_contact_queryset, get_public_offer_queryset, get_about_las_active, \
    get_magazine_queryset, get_requisite_queryset


class ContactListView(ListModelMixin, GenericViewSet):
    serializer_class = ContactListSerializer
    permission_classes = (AllowAny, )
    queryset = get_contact_queryset()
    pagination_class = None


class PublicOfferListView(ListModelMixin, GenericViewSet):
    serializer_class = PublicOfferListSerializer
    permission_classes = (AllowAny, )
    queryset = get_public_offer_queryset()
    pagination_class = None


class AboutView(APIView):

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    @swagger_auto_schema(
        responses={200: AboutSerializer()}
    )
    def get(self, request):
        qs = get_about_las_active()
        if qs.exists():
            return Response(AboutSerializer(qs.last(), context=self.get_serializer_context()).data)
        return Response({'message': 'not_found'}, status=HTTP_404_NOT_FOUND)


class MagazineViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = MagazineSerializer
    queryset = get_magazine_queryset().order_by('-created_at')


class RequisiteViewSet(ListModelMixin, GenericViewSet):
    serializer_class = RequisiteSerializer
    queryset = get_requisite_queryset().order_by('position')
    pagination_class = None
