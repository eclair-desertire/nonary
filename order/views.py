import json
import xml.etree.ElementTree as ET

import requests
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.db.transaction import atomic
from django.template import loader
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from order.filters import HistoryFilter
from order.models import Order
from order.serializers import AddToBasketSerializer, AddToBasketResponseSerializer, BasketDetailSerializer, \
    CreateOrderSerializer, AddPromoToOrderSerializer, OrderCreateSerializer, ChangeOrderDeliverySerializer, \
    OrderPriceInfoSerializer, OrderDetailSerializer, OrderDetailHistorySerializer, OrderListHistorySerializer, \
    CopyOrderSerializer, OrderPriceInfoSerializerResponse, PayOrderSerializer
from order.services.client.basket import add_product_to_basket, get_basket_info, clear_basket
from order.services.client.orders import assign_user_to_order, create_order, get_order_history, add_promo, \
    create_order_without_basket, change_order_delivery, get_order_for_calculation_info, prefetch_order_history, \
    copy_order
from order.services.client.payment import pay_with_token, pay_with_new_card
from order.services.common import send_webkassa
from utils.choices import PaymentTypeChoice, OrderStatusChoices
from utils.custom_logging import save_info, save_warning
from utils.manual_parameters import QUERY_CITY_SLUG, QUERY_ORDER_STATUS


class AddBasketItemView(APIView):

    @swagger_auto_schema(
        request_body=AddToBasketSerializer(),
        responses={200: AddToBasketResponseSerializer()}
    )
    def post(self, request):
        serializer = AddToBasketSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        basket = add_product_to_basket(request.user, serializer.validated_data)
        return Response({
            'token': basket.token
        })


class BasketDetailView(APIView):

    @swagger_auto_schema(
        responses={200: BasketDetailSerializer()},
        manual_parameters=[QUERY_CITY_SLUG]
    )
    def get(self, request, token):
        city_slug = request.query_params.get('city_slug', None)
        if token == 'null':
            token = None
        instance = get_object_or_404(get_basket_info(token, request.user, city_slug=city_slug), **{'token': token})
        return Response(BasketDetailSerializer(instance, context={'request': request}).data)


class SetUserToBasket(APIView):
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        request_body=AddToBasketResponseSerializer()
    )
    def post(self, request):
        serializer = AddToBasketResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        assign_user_to_order(request.user, serializer.validated_data)
        return Response({'message': 'OK'})


class ChangeOrderDeliveryView(APIView):
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        request_body=ChangeOrderDeliverySerializer(),
        responses={200: OrderPriceInfoSerializerResponse()}
    )
    def post(self, request, token):
        if token == 'null':
            token = None
        serializer = ChangeOrderDeliverySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = change_order_delivery(request.user, token, serializer.validated_data)
        order = get_order_for_calculation_info({'id': instance.id})
        serializer = OrderPriceInfoSerializer(order)
        return Response(serializer.data)


class CreateOrderView(APIView):
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        request_body=CreateOrderSerializer()
    )
    def post(self, request, token):
        if token == 'null':
            token = None
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        with atomic():
            order = create_order(request.user, token, serializer.validated_data)
            pay_url = None
            if order.payment.payment_type == PaymentTypeChoice.CARD:
                current_site = get_current_site(request)
                protocol = 'https' if request.is_secure() else 'http'
                current_site = f"{protocol}://{current_site}"
                if order.card:
                    pay_with_token(current_site, order)
                else:
                    pay_url = pay_with_new_card(current_site, order)
            else:
                # order.is_basket = False
                order.status = OrderStatusChoices.NEW
                order.save()
            return Response({'url': pay_url, 'id': order.id})


class PayOrderView(APIView):

    @swagger_auto_schema(
        request_body=PayOrderSerializer()
    )
    def post(self, request):
        serializer = PayOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.validated_data.get('order')
        pay_url = None
        if order.payment.payment_type == PaymentTypeChoice.CARD:
            current_site = get_current_site(request)
            protocol = 'https' if request.is_secure() else 'http'
            current_site = f"{protocol}://{current_site}"
            pay_url = pay_with_new_card(current_site, order)
        return Response({'url': pay_url, 'id': order.id})


class OrderCreateNoBasketView(APIView):
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        request_body=OrderCreateSerializer()
    )
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = create_order_without_basket(serializer.validated_data, request.user)
        # here should be payment logic
        return Response({'order_id': order.order_id})


class OrderHistoryView(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    permission_classes = (IsAuthenticated, )
    serializer_class = OrderListHistorySerializer
    filter_backends = (DjangoFilterBackend, SearchFilter,)
    filterset_class = HistoryFilter
    search_fields = ('order_id', )

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderDetailHistorySerializer
        return super(OrderHistoryView, self).get_serializer_class()

    def get_queryset(self):
        if self.request.user.is_authenticated:
            queryset = get_order_history(self.request.user)
            if self.action == 'retrieve':
                queryset = prefetch_order_history(queryset)

            return queryset
        return Order.objects.none()

    @swagger_auto_schema(
        manual_parameters=[QUERY_ORDER_STATUS]
    )
    def list(self, request, *args, **kwargs):
        return super(OrderHistoryView, self).list(request, *args, **kwargs)


class GetOrderPriceInfo(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        responses={200: OrderPriceInfoSerializerResponse()}
    )
    def get(self, request, token):
        order = get_order_for_calculation_info({'token': token})
        serializer = OrderPriceInfoSerializer(order)
        return Response(serializer.data)


class AddPromoToOrderView(APIView):

    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        request_body=AddPromoToOrderSerializer(),
        responses={200: OrderPriceInfoSerializerResponse()}
    )
    def post(self, request):
        serializer = AddPromoToOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = add_promo(request.user, serializer.validated_data)
        order = get_order_for_calculation_info({'id': instance.id})
        serializer = OrderPriceInfoSerializer(order)
        return Response(serializer.data)


class FortePaymentTestView(APIView):

    permission_classes = (AllowAny, )

    def get(self, request):
        current_site = get_current_site(request)
        protocol = 'https' if request.is_secure() else 'http'
        context = {
            'operation': 'CreateOrder',
            'order_type': 'Purchase',
            'merchant': 'SMALL_TEST',
            'amount': '10000.0',
            'currency': '398',
            'order_description': 'xxx',
            'approve_url': f'{protocol}://{current_site}/api/order/payment-success/{request.user.id}/',
            'cancel_url': f'{protocol}://{current_site}/api/order/payment-cancel/{request.user.id}/',
            'decline_url': f'{protocol}://{current_site}/api/order/payment-decline/{request.user.id}/',
            'customer_contact': request.user.email if request.user.email else request.user.phone_number,
        }

        headers = {'Content-Type': 'application/xml'}  # set what your server accepts
        xml = loader.render_to_string(
            'create_order.xml',
            context
        )
        resp = requests.post(f'{settings.PAYMENT_URL}', data=xml, headers=headers)
        tree = ET.ElementTree(ET.fromstring(resp.text))
        response = tree.find('Response')
        if response:
            order = response.find('Order')
            if order:
                payment_order_id = order.find('OrderID').text
                session_id = order.find('SessionID').text
                url = order.find('URL').text
                if payment_order_id and session_id and url:
                    # instance.payment_order_id = payment_order_id
                    # instance.save()
                    return Response({
                        'redirect_to': f'{url}?OrderID={payment_order_id}&SessionID={session_id}'
                    })
        return Response(resp.text, status=resp.status_code, content_type='application/xml')


class CardRegistrationWebhook(APIView):

    def post(self, request, payment_status, order_id):
        text_msg = payment_status
        instance = Order.objects.get(id=order_id)
        if payment_status == 'success':
            xml_out = ET.fromstring(request.data.get('xmlmsg'))
            text_msg = request.data.get('xmlmsg')
            message = xml_out.find('Message')
            if message is not None:
                order_status = message.find('OrderStatus')
                if order_status is not None and order_status.text == 'APPROVED':
                    instance.paid = True
                    # instance.is_basket = False
                    instance.status = OrderStatusChoices.NEW
                    instance.save()
                    send_webkassa(instance)
                    save_info(f'Order with id={instance.id}, changed status to PAID')
                    text_msg = order_status.text
                elif order_status is not None:
                    save_warning(f'Order status is {order_status.text}')
                    text_msg = request.data.get('xmlmsg')
                else:
                    save_warning(f"OrderStatus is None")
            else:
                save_warning(f"Message is None")
        elif payment_status == 'cancel':
            instance.is_basket = True
            instance.save()
        elif payment_status == 'decline':
            instance.is_basket = True
            instance.save()
        return Response({'message': text_msg})

    def get(self, request, payment_status, order_id):
        save_info(f"{payment_status}: {json.dumps(request.query_params.dict())}")
        instance = Order.objects.get(id=order_id)
        if payment_status == 'cancel':
            instance.is_basket = True
            instance.save()
        elif payment_status == 'decline':
            instance.is_basket = True
            instance.save()
        return Response({'message': 'Declined/Canceled'})


class OrderInfoView(APIView):

    @swagger_auto_schema(
        responses={200: OrderDetailSerializer()}
    )
    def get(self, request, pk):
        instance = get_order_for_calculation_info({'pk': pk})
        serializer = OrderDetailSerializer(instance)
        return Response(serializer.data)


class CopyOrderView(APIView):

    @swagger_auto_schema(
        request_body=CopyOrderSerializer(),
        responses={200: AddToBasketResponseSerializer()}
    )
    def post(self, request):
        serializer = CopyOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        qs = prefetch_order_history(get_order_history(request.user))
        instance = get_object_or_404(qs, id=serializer.validated_data.get('order'))
        basket = copy_order(instance)
        return Response({
            'token': basket.token
        })


class ClearBasket(APIView):

    def delete(self, request, token):
        clear_basket(token)
        return Response(status=HTTP_204_NO_CONTENT)
