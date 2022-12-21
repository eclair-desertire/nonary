from django_filters import rest_framework as filters

from shop.models import Category, Subcategory, Product, ProductReview, ChildCategory, Brand, Compilation


class ChildCategoryFilter(filters.FilterSet):
    category = filters.CharFilter(field_name='category__slug')

    class Meta:
        model = ChildCategory
        fields = ['category']


class BrandFilter(filters.FilterSet):
    category = filters.CharFilter(field_name='products__categories__category__slug')

    class Meta:
        model = Brand
        fields = ['category']


class CompilationFilter(filters.FilterSet):
    category = filters.CharFilter(field_name='products__categories__category__slug')

    class Meta:
        model = Compilation
        fields = ['category']


class SubcategoryFilter(filters.FilterSet):
    category = filters.CharFilter(field_name='category__slug')

    class Meta:
        model = Subcategory
        fields = ['category']


class ProductFilter(filters.FilterSet):
    brand = filters.CharFilter(field_name='brand__slug')
    category = filters.CharFilter(field_name='categories__category__slug')
    level3 = filters.CharFilter(field_name='categories__slug')
    price_min = filters.NumberFilter(field_name='discount_price', lookup_expr='gte')
    price_max = filters.NumberFilter(field_name='discount_price', lookup_expr='lte')

    class Meta:
        model = Product
        fields = ['brand', 'category', 'stocks', 'level3', 'price_min', 'price_max']


class ReviewFilter(filters.FilterSet):
    class Meta:
        model = ProductReview
        fields = ['product']
        