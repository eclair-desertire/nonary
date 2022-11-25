from django import forms
from django.contrib import admin

from shop.forms import BrandForm
from shop.models import (
    Category, Subcategory, Brand, ChildCategory, Product, Property, ProductProperty, Delivery, Storehouse,
    ProductPrice, Payment, Rest, Compilation, ProductImage, PropertyValue
)


class SubcategoryTabular(admin.TabularInline):
    model = Subcategory


class ProductImageTabular(admin.TabularInline):
    model = ProductImage


class ChildCategoryTabular(admin.TabularInline):
    model = ChildCategory


class ProductPropertyTabular(admin.TabularInline):
    model = ProductProperty

#
# class ProductInline(admin.TabularInline):
#     model = Product


class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'image', 'created_at', 'is_active', 'is_top',)
    list_display_links = ('name', 'slug', 'image', 'created_at', 'is_active', 'is_top',)
    list_filter = ('is_active', 'is_top',)
    search_fields = ('name', )

    form = BrandForm

    # inlines = [ProductInline]

    fieldsets = (
        (None, {'fields': ('name', 'image', 'is_active', 'is_top', 'products')}),
        ('Даты', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ('created_at', 'updated_at',)


class CategoryBrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'image', 'created_at', 'is_active',)
    list_display_links = ('name', 'slug', 'image', 'created_at', 'is_active',)
    list_filter = ('is_active',)
    search_fields = ('name', )

    fieldsets = (
        (None, {'fields': ('name', 'image', 'is_active', )}),
        ('Даты', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ('created_at', 'updated_at',)


@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'price', 'delivery_type', 'created_at', 'is_active')
    list_display_links = ('name', 'city', 'price', 'delivery_type', 'created_at', 'is_active')
    list_filter = ('is_active', 'delivery_type', 'city')
    search_fields = ('name', )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('name', 'payment_type', 'created_at', 'is_active')
    list_display_links = ('name', 'payment_type', 'created_at', 'is_active')
    list_filter = ('is_active', 'payment_type',)
    search_fields = ('name', )


@admin.register(ProductProperty)
class ProductPropertyAdmin(admin.ModelAdmin):
    list_display = ('product', 'property_value', 'created_at', 'is_active')
    list_display_links = ('product', 'property_value',  'created_at', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('product__name', )

    fieldsets = (
        (None, {'fields': ('product', 'property_value',  'is_active')}),
        ('Даты', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ('created_at', 'updated_at',)


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'property_type', 'created_at', 'is_active')
    list_display_links = ('name', 'slug', 'property_type', 'created_at', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)

    fieldsets = (
        (None, {'fields': ('name', 'property_type', 'is_active', 'position',)}),
        ('Даты', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ('created_at', 'updated_at',)


@admin.register(Category)
class CategoryAdmin(CategoryBrandAdmin):
    inlines = [SubcategoryTabular]


@admin.register(ChildCategory)
class ChildCategoryAdmin(CategoryBrandAdmin):
    list_display = ('name', 'slug', 'category', 'created_at', 'is_active')
    list_display_links = ('name', 'slug', 'category', 'created_at', 'is_active')
    list_filter = ('is_active', 'category')
    search_fields = ('name',)

    fieldsets = (
        (None, {'fields': ('name', 'category', 'is_active')}),
        ('Даты', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ('created_at', 'updated_at',)


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'image', 'category', 'created_at', 'is_active')
    list_display_links = ('name', 'slug', 'image', 'category', 'created_at', 'is_active')
    list_filter = ('is_active', 'category')
    search_fields = ('name',)
    inlines = [ChildCategoryTabular]

    fieldsets = (
        (None, {'fields': ('name', 'image', 'category', 'is_active')}),
        ('Даты', {'fields': ('created_at', 'updated_at')}),
    )

    def get_queryset(self, request):
        qs = super(SubcategoryAdmin, self).get_queryset(request)
        return qs.select_related('category')

    readonly_fields = ('created_at', 'updated_at',)


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ProductAdminForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['similar_products'].queryset = self.fields['similar_products'].queryset.filter(
                categories__in=self.instance.categories.all(), main_products__isnull=True
            ).exclude(
                pk=self.instance.pk
            )
            self.fields['same_products'].queryset = self.fields['same_products'].queryset.filter(
                main_products__isnull=True,
                categories__in=self.instance.categories.all()  # tmp, do not forget remove this
            ).exclude(
                pk=self.instance.pk
            )


@admin.register(PropertyValue)
class PropertyValueAdmin(admin.ModelAdmin):
    list_display = ('property', 'value', 'hex_value',)
    list_display_links = ('property', 'value', 'hex_value',)
    list_filter = ('property',)
    search_fields = ('value', 'property__name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at', 'is_active', 'image',)
    list_display_links = ('name', 'slug', 'created_at', 'is_active')
    list_filter = ('is_active', 'compilations', 'categories')
    list_editable = ('image', )
    search_fields = ('name',)
    filter_horizontal = ('deliveries', 'similar_products', 'same_products', 'similar_properties')
    form = ProductAdminForm

    def has_add_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        queryset = super(ProductAdmin, self).get_queryset(request)
        queryset = queryset.filter(main_products__isnull=True).prefetch_related('categories')
        return queryset

    inlines = [ProductImageTabular, ProductPropertyTabular]

    fieldsets = (
        (None, {'fields': ('name', 'categories', 'brand', 'is_active', 'description', 'image',)}),
        ('Вариации товара', {'fields': ('similar_products', 'similar_properties')}),
        ('Похожие товары', {'fields': ('same_products',)}),
        ('Способы доставки', {'fields': ('deliveries', )}),
        ('Даты', {'fields': ('created_at', 'updated_at')}),
        ('Данные 1С', {'fields': ('version', 'barcode', 'vendor_code', 'weight', 'base_unit', 'external_id')}),
    )

    readonly_fields = (
        'created_at', 'updated_at', 'version', 'barcode', 'vendor_code', 'weight', 'base_unit', 'external_id'
    )


@admin.register(Storehouse)
class StorehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'external_id', 'storehouse_type', 'created_at', 'is_active')
    list_display_links = ('name', 'external_id', 'storehouse_type', 'created_at', 'is_active')
    list_filter = ('is_active',)

    fieldsets = (
        (None, {'fields': ('name', 'external_id', 'storehouse_type', 'is_active')}),
        ('Даты', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ('name', 'created_at', 'updated_at', 'external_id', 'storehouse_type', 'is_active',)


@admin.register(ProductPrice)
class ProductPriceAdmin(admin.ModelAdmin):
    list_display = ('product', 'storehouse', 'price', 'created_at', 'is_active')
    list_display_links = ('product', 'storehouse', 'price', 'created_at', 'is_active')
    list_filter = ('is_active',)

    fieldsets = (
        (None, {'fields': ('product', 'storehouse', 'price', 'is_active')}),
        ('Даты', {'fields': ('created_at', 'updated_at')}),
    )

    readonly_fields = ('created_at', 'updated_at', 'product', 'storehouse', 'price', 'is_active')

    def get_queryset(self, request):
        qs = super(ProductPriceAdmin, self).get_queryset(request)
        return qs.select_related('storehouse', 'product')


@admin.register(Compilation)
class CompilationAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'get_compilation_type_display', 'position')
    list_display_links = ('name', 'created_at', 'get_compilation_type_display')
    list_editable = ('position', 'is_active')

    list_filter = ('is_active', 'compilation_type')

    fieldsets = (
        (None, {'fields': ('name', 'compilation_type', 'position', 'is_active', 'products')}),
        ('Даты', {'fields': ('created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at', )
    filter_horizontal = ('products', )


admin.site.register(Brand, BrandAdmin)
admin.site.register(Rest)

