from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from imagekit.models import ProcessedImageField

from utils.choices import BaseUnitChoices, PropertyTypeChoices, DeliveryTypeChoice, StorehouseTypeChoices, \
    PaymentTypeChoice, CompilationTypeChoices
from utils.models import BaseModel, SlugModel


User = get_user_model()


class Category(SlugModel):
    image = ProcessedImageField(upload_to='category', processors=[], format='WEBP', options={'quality': 60}, null=True,
                                blank=True)
    external_id = models.CharField(max_length=1000, verbose_name='ИД в 1с')
    version = models.CharField(max_length=1000, verbose_name='Номер Версии', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категорию 1-го уровня'
        verbose_name_plural = 'Категории 1-го уровня'


class Subcategory(SlugModel):
    image = ProcessedImageField(upload_to='subcategory', processors=[], format='WEBP', options={'quality': 60}, null=True,
                                blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    external_id = models.CharField(max_length=1000, verbose_name='ИД в 1с')
    version = models.CharField(max_length=1000, verbose_name='Номер Версии', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категорию 2-го уровня'
        verbose_name_plural = 'Категории 2-го уровня'


class ChildCategory(SlugModel):
    category = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name='child_categories')
    external_id = models.CharField(max_length=1000, verbose_name='ИД в 1с')
    version = models.CharField(max_length=1000, verbose_name='Номер Версии', blank=True, null=True)
    image = ProcessedImageField(upload_to='child_category', processors=[], format='WEBP', options={'quality': 60},
                                null=True,
                                blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категорию 3-го уровня'
        verbose_name_plural = 'Категории 3-го уровня'


class Brand(SlugModel):
    image = ProcessedImageField(upload_to='brand', processors=[], format='WEBP', options={'quality': 60}, null=True,
                                blank=True)
    is_top = models.BooleanField(default=False, verbose_name='В списке топ?')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'


class Product(SlugModel):
    version = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Версия')
    barcode = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Штрихкод')
    vendor_code = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Артикул')
    weight = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Вес')
    base_unit = models.CharField(max_length=10, choices=BaseUnitChoices.choices, default=BaseUnitChoices.PIECE,
                                 verbose_name='Базовая единица')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, blank=True, null=True, verbose_name='Бренд',
                              related_name='products')
    categories = models.ManyToManyField(ChildCategory, related_name='products', verbose_name='Категории')
    external_id = models.CharField(max_length=1000, verbose_name='ИД в 1с')
    similar_products = models.ManyToManyField('self', blank=True, verbose_name='Другие характеристики',
                                              symmetrical=False, related_name='main_products')
    similar_properties = models.ManyToManyField('shop.Property', blank=True, verbose_name='Объединить характеристики',
                                                related_name='similar_products')
    same_products = models.ManyToManyField('self', blank=True, verbose_name='Похожие')
    in_store_date = models.DateField(default=timezone.now)
    deliveries = models.ManyToManyField('shop.Delivery', related_name='products', verbose_name='Способы доставки')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    image = models.URLField(max_length=1000, verbose_name='Ссылка на главную картинку', blank=True, null=True)
    prices_dict = models.JSONField(default=dict)
    rests_dict = models.JSONField(default=dict)

    def clean(self):
        if self.similar_properties.count() > 2:
            raise ValidationError("Нельзя использовать более чем 2 параметра для выборки! Дизайн не позволяет")
        super(Product, self).clean()

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

    def __str__(self):
        return self.name

    @property
    def is_new(self):
        today = timezone.now().date()
        return (today - self.in_store_date).total_seconds() // (3600*24) <= 30


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='Товар')
    image = models.URLField(max_length=1000, verbose_name='Ссылка на картинку', blank=True, null=True)

    class Meta:
        verbose_name = 'Картинку товара'
        verbose_name_plural = 'Картинки товара'


class Storehouse(BaseModel):
    external_id = models.CharField(max_length=1000, verbose_name='ИД в 1с')
    storehouse_type = models.CharField(max_length=15, choices=StorehouseTypeChoices.choices,
                                       default=StorehouseTypeChoices.BASIC)
    name = models.CharField(max_length=255, verbose_name='Название')
    version = models.CharField(max_length=1000, blank=True, null=True, verbose_name='Версия')

    class Meta:
        verbose_name = 'Склад'
        verbose_name_plural = 'Склады'

    def __str__(self):
        return self.name if self.name else self.external_id


class ProductPrice(BaseModel):
    storehouse = models.ForeignKey(Storehouse, on_delete=models.CASCADE, related_name='products', verbose_name='Склад')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='prices', verbose_name='Товар')
    price = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Цена', default="0.0")

    class Meta:
        verbose_name = 'Цену'
        verbose_name_plural = 'Цены'

    def __str__(self):
        return f"{self.storehouse.external_id} - {self.product.name}"


class Property(SlugModel):
    property_type = models.CharField(max_length=20, choices=PropertyTypeChoices.choices,
                                     default=PropertyTypeChoices.STRING)
    # is_multiple = models.BooleanField(default=False, verbose_name='Для выборки')

    class Meta:
        verbose_name = 'Характеристику'
        verbose_name_plural = 'Характеристики'

    def __str__(self):
        return self.name


class PropertyValue(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='values',
                                 verbose_name='Характеристика')
    value = models.CharField(max_length=1000, verbose_name='Значение', default='', blank=True, null=True)
    hex_value = models.CharField(max_length=25, verbose_name='Значение цвета', blank=True, null=True,
                                 help_text='Если нужно отрисовать цвет!')

    def __str__(self):
        return f"{self.property.name} - {self.value}"

    class Meta:
        verbose_name = 'Значение характеристики'
        verbose_name_plural = 'Значения характеристик'


class ProductProperty(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='properties', verbose_name='Товар')
    property_value = models.ForeignKey(PropertyValue, on_delete=models.CASCADE, related_name='products',
                                       verbose_name='Значение характеристики', null=True)
    # value = models.CharField(max_length=1000, verbose_name='Значение', default='', blank=True, null=True)

    class Meta:
        verbose_name = 'Характеристику товара'
        verbose_name_plural = 'Характеристики товара'


class Delivery(BaseModel):
    name = models.CharField(max_length=200, verbose_name='Название')
    city = models.ForeignKey('location.City', on_delete=models.CASCADE, related_name='deliveries',
                             verbose_name='Город')
    price = models.DecimalField(max_digits=14, decimal_places=2, verbose_name='Цена доставки')
    delivery_type = models.CharField(max_length=20, choices=DeliveryTypeChoice.choices,
                                     default=DeliveryTypeChoice.COURIER, verbose_name='Тип доставки')
    commerceml_id = models.CharField(max_length=255, blank=True, null=True, verbose_name='Место доставки ИД',
                                     help_text='Используется если доставка курьером')

    class Meta:
        verbose_name = 'Доставку'
        verbose_name_plural = 'Доставки'

    def __str__(self):
        return f"{self.name} ({self.get_delivery_type_display()})"


class ProductReview(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='reviews')
    stars = models.IntegerField(default=5)
    text = models.TextField()


class ReviewImage(BaseModel):
    review = models.ForeignKey(ProductReview, on_delete=models.CASCADE, related_name='images')
    image = ProcessedImageField(upload_to='review', processors=[], format='WEBP', options={'quality': 60}, null=True,
                                blank=True)


class ReviewUseful(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='useful_reviews')
    review = models.ForeignKey(ProductReview, on_delete=models.CASCADE, related_name='useful_users')
    is_useful = models.BooleanField(default=True)


class Payment(BaseModel):
    name = models.CharField(max_length=200, verbose_name='Название')
    # city = models.ForeignKey('location.City', on_delete=models.CASCADE, related_name='deliveries',
    #                          verbose_name='Город')
    payment_type = models.CharField(max_length=20, choices=PaymentTypeChoice.choices,
                                    default=PaymentTypeChoice.CASH, verbose_name='Тип оплаты')

    class Meta:
        verbose_name = 'Способ оплаты'
        verbose_name_plural = 'Способы оплаты'

    def __str__(self):
        return f"{self.name} ({self.get_payment_type_display()})"


class UserSeenProduct(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='seen_users')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seen_products')


class ImportStatus(BaseModel):
    filename = models.CharField(max_length=255, unique=True)


class Rest(models.Model):
    storehouse = models.ForeignKey(Storehouse, on_delete=models.CASCADE, related_name='product_rests')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='rests')
    quantity = models.IntegerField(default=0)


class Compilation(BaseModel):
    name = models.CharField(max_length=255, verbose_name='Название')
    products = models.ManyToManyField(Product, related_name='compilations', verbose_name='Товары', blank=True)
    compilation_type = models.CharField(max_length=15, choices=CompilationTypeChoices.choices,
                                        default=CompilationTypeChoices.MANUAL, verbose_name='Тип подборки')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Выборку'
        verbose_name_plural = 'Выборки'
        ordering = ('position', )


# for good in products:
#     prices = ProductPrices.objects.filter(product=good)
#     prices_dict = {}
#     for price in prices:
#         cities = price.storehouse.cities.all()
#         for city in cities:
#             prices_dict.update({
#                  f"{city.slug}_{price.storehouse.storehouse_type}": price.price
#             })
