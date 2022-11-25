from utils.crud import create_object
from django.apps import apps


ChildCategory = apps.get_model(app_label='shop', model_name='ChildCategory')
Product = apps.get_model(app_label='shop', model_name='Product')


def create_product(product_data):
    return create_object('shop', 'Product', product_data)


def _get_good_categories(categories_id):
    return ChildCategory.objects.filter(external_id__in=categories_id)
