from decimal import Decimal

from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from rest_framework import serializers

from shop.models import Product, ReviewImage, ProductReview, ReviewUseful, Payment
from shop.services.client.serialized_data import get_properties, reformat_properties
from utils.serializers import BaseSerializer


class CategorySerializer(BaseSerializer):
    name = serializers.CharField()
    slug = serializers.CharField()
    image = serializers.ImageField()


class ChildCategorySerializer(BaseSerializer):
    name = serializers.CharField()
    slug = serializers.CharField()
    image = serializers.ImageField()


class SubcategoryDetailSerializer(CategorySerializer):
    category_name = serializers.CharField()
    category_slug = serializers.CharField()


class BrandListSerializer(BaseSerializer):
    id = serializers.IntegerField()
    image = serializers.ImageField()
    name = serializers.CharField()
    slug = serializers.CharField()


class PropertySerializer(BaseSerializer):
    id = serializers.IntegerField()
    slug = serializers.CharField()
    name = serializers.CharField()
    property_type = serializers.CharField()


class ProductPropertyListSerializer(BaseSerializer):
    id = serializers.IntegerField()
    value = serializers.CharField()
    property = PropertySerializer()


class ProductImageSerializer(BaseSerializer):
    id = serializers.IntegerField()
    image = serializers.URLField()


class ProductListSerializer(BaseSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    slug = serializers.CharField()
    version = serializers.CharField()
    barcode = serializers.CharField()
    vendor_code = serializers.CharField()
    weight = serializers.CharField()
    base_unit = serializers.CharField()
    brand = BrandListSerializer()
    is_favourite = serializers.BooleanField()
    rating = serializers.FloatField()
    price = serializers.DecimalField(max_digits=14, decimal_places=2)
    discount_price = serializers.DecimalField(max_digits=14, decimal_places=2)
    comments = serializers.IntegerField()
    is_new = serializers.BooleanField()
    discount = serializers.SerializerMethodField()
    external_id = serializers.CharField()
    rest = serializers.IntegerField()
    image = serializers.URLField(read_only=True)

    def get_discount(self, instance):
        if instance.discount_price:
            return "%.2f" % (100 - (instance.discount_price * 100) / instance.price)
        return "%.2f" % 0.0


class ProductDetailSerializer(ProductListSerializer):
    properties = serializers.SerializerMethodField()
    description = serializers.CharField()
    categories = ChildCategorySerializer(many=True)
    brand = BrandListSerializer()
    images = ProductImageSerializer(many=True)

    def get_properties(self, instance):
        similar_properties = []
        if hasattr(instance, 'similar_property_list'):
            similar_properties = [item.id for item in instance.similar_property_list]
        properties = get_properties(instance, {}, similar_properties, ProductImageSerializer)
        if hasattr(instance, 'similar_list'):
            for item in instance.similar_list:
                properties = get_properties(item, properties, similar_properties, ProductImageSerializer)
        return reformat_properties(properties)


class PropertyValueResponseSerializer(BaseSerializer):
    value = serializers.CharField()
    product_id = serializers.IntegerField()


class ProductPropertiesResponseSerializer(BaseSerializer):
    property_name = PropertyValueResponseSerializer(many=True)


class ProductDetailResponseSerializer(ProductListSerializer):
    properties = ProductPropertiesResponseSerializer()


class FavouriteProductSerializer(BaseSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.filter(is_active=True))


class DeliveryListSerializer(BaseSerializer):
    name = serializers.CharField()
    price = serializers.DecimalField(max_digits=14, decimal_places=2)
    delivery_type = serializers.CharField()


class DeliveryQuerySerializer(BaseSerializer):
    city_slug = serializers.CharField()


class AuthorSerializer(BaseSerializer):
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    class Meta:
        ref_name = 'ReviewAuthorSerializer'


class ReviewImageSerializer(BaseSerializer):
    id = serializers.IntegerField()
    image = serializers.ImageField()


class ReviewListSerializer(BaseSerializer):
    id = serializers.IntegerField(read_only=True)
    answered = serializers.BooleanField(read_only=True)
    user = AuthorSerializer(read_only=True)
    stars = serializers.IntegerField()
    text = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)
    image_list = ReviewImageSerializer(many=True)
    likes = serializers.IntegerField()


class ReviewCreateSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        file_fields = kwargs.pop('file_fields', None)
        super().__init__(*args, **kwargs)
        if file_fields:
            field_update_dict = {field: serializers.FileField(required=False, write_only=True) for field in file_fields}
            self.fields.update(**field_update_dict)

    def create(self, validated_data):
        validated_data_copy = validated_data.copy()
        validated_files = []

        for key, value in validated_data_copy.items():
            if isinstance(value, InMemoryUploadedFile) or isinstance(value, TemporaryUploadedFile):
                validated_files.append(value)
                validated_data.pop(key)
        review_instance = super().create(validated_data)
        for file in validated_files:
            ReviewImage.objects.create(review=review_instance, image=file)
        return review_instance

    image_1 = serializers.ImageField(required=False)
    image_2 = serializers.ImageField(required=False)
    image_3 = serializers.ImageField(required=False)
    image_4 = serializers.ImageField(required=False)
    image_5 = serializers.ImageField(required=False)
    stars = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = ProductReview
        fields = ('stars', 'text', 'product', 'image_1', 'image_2', 'image_3', 'image_4', 'image_5')


class UsefulReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewUseful
        exclude = ('user', 'is_active', 'position')


class ProductCountSerializer(BaseSerializer):
    count = serializers.IntegerField()


class SimilarProductQuerySerializer(BaseSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all().prefetch_related('categories').select_related('brand'))


class PaymentListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = '__all__'


class CompilationSerializer(BaseSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
