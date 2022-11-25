from rest_framework import serializers
from utils.serializers import BaseSerializer


class ExportOrderUserSerializer(BaseSerializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    phone_number = serializers.CharField()


class ExportOrderProductSerializer(BaseSerializer):
    external_id = serializers.CharField()
    vendor_code = serializers.CharField()
    name = serializers.CharField()
    price = serializers.DecimalField(max_digits=14, decimal_places=2)


class ExportOrderItemSerializer(BaseSerializer):
    product = ExportOrderProductSerializer()
    quantity = serializers.IntegerField()
    discount = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    def get_discount(self, instance):
        pass

    def get_total_price(self, instance):
        pass


class ExportOrderSerializer(BaseSerializer):
    order_id = serializers.CharField()
    created_at = serializers.DateTimeField()
    total_price = serializers.DecimalField(max_digits=14, decimal_places=2)
    comment = serializers.CharField()
    user = ExportOrderUserSerializer()
    full_address = serializers.SerializerMethodField()
    post_index = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    delivery_type = serializers.SerializerMethodField()
    delivery_price = serializers.SerializerMethodField()
    item_list = ExportOrderItemSerializer(many=True)
    status = serializers.SerializerMethodField()
    payment_method = serializers.SerializerMethodField()
    delivery_method = serializers.SerializerMethodField()
    delivery_id = serializers.SerializerMethodField()
    payment_status = serializers.SerializerMethodField()

    def get_full_address(self, instance):
        pass

    def get_post_index(self, instance):
        pass

    def get_country(self, instance):
        return 'Казахстан'

    def get_city(self, instance):
        return 'Алматы'

    def get_address(self, instance):
        pass

    def get_delivery_type(self, instance):
        pass

    def get_delivery_price(self, instance):
        pass

    def get_status(self, instance):
        pass

    def get_payment_method(self, instance):
        pass

    def get_delivery_method(self, instance):
        pass

    def get_delivery_id(self, instance):
        pass

    def get_payment_status(self, instance):
        pass
