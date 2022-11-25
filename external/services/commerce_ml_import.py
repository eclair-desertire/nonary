import os
from collections import OrderedDict
from xml.etree import ElementTree

import after_response
from django.apps import apps

from shop.models import PropertyValue
from utils.choices import StorehouseTypeChoices
from utils.crud import update_object
from utils.statics import ORDER_STATUS_TRANSLATES
from utils.utils import is_camel_case


Product = apps.get_model(app_label='shop', model_name='Product')
City = apps.get_model(app_label='location', model_name='City')
Storehouse = apps.get_model(app_label='shop', model_name='Storehouse')
ProductPrice = apps.get_model(app_label='shop', model_name='ProductPrice')
ImportStatus = apps.get_model(app_label='shop', model_name='ImportStatus')
Rest = apps.get_model(app_label='shop', model_name='Rest')
Property = apps.get_model(app_label='shop', model_name='Property')
ProductProperty = apps.get_model(app_label='shop', model_name='ProductProperty')
ChildCategory = apps.get_model(app_label='shop', model_name='ChildCategory')
Category = apps.get_model(app_label='shop', model_name='Category')
Subcategory = apps.get_model(app_label='shop', model_name='Subcategory')
Order = apps.get_model(app_label='order', model_name='Order')


def _get_instance_data(item):
    return {
        'name': item.find('{urn:1C.ru:commerceml_3}Наименование').text,
        'version': item.find('{urn:1C.ru:commerceml_3}НомерВерсии').text,
        'is_active': item.find('{urn:1C.ru:commerceml_3}ПометкаУдаления').text == 'false'
    }


@after_response.enable
def fetch_storehouse_from_xml(xml_path, filename):
    tree = ElementTree.parse(xml_path)
    for node in tree.findall('{urn:1C.ru:commerceml_3}Классификатор'):
        for item in node.find('{urn:1C.ru:commerceml_3}ТипыЦен'):
            storehouse_type = StorehouseTypeChoices.DISCOUNT
            sklad_id = item.find('{urn:1C.ru:commerceml_3}Ид').text
            if 'NOdc' in sklad_id:
                storehouse_type = StorehouseTypeChoices.BASIC
            storehouse, _ = Storehouse.objects.get_or_create(external_id=sklad_id, storehouse_type=storehouse_type)
            storehouse_data = _get_instance_data(item)
            update_object(storehouse, OrderedDict(storehouse_data))
    os.remove(xml_path)
    ImportStatus.objects.filter(filename=filename).delete()


@after_response.enable
def fetch_categories_from_xml(xml_path, filename=''):
    tree = ElementTree.parse(xml_path)
    for node in tree.findall('{urn:1C.ru:commerceml_3}Классификатор'):
        for item in node.find('{urn:1C.ru:commerceml_3}Группы'):
            category, _ = Category.objects.get_or_create(external_id=item.find('{urn:1C.ru:commerceml_3}Ид').text)
            category_data = _get_instance_data(item)
            category = update_object(category, OrderedDict(category_data))
            for sub_item in item.find('{urn:1C.ru:commerceml_3}Группы'):
                subcategory, _ = Subcategory.objects.get_or_create(
                    external_id=sub_item.find('{urn:1C.ru:commerceml_3}Ид').text,
                    category=category
                )
                subcategory_data = {
                    'category': category,
                    **_get_instance_data(sub_item)
                }
                subcategory = update_object(subcategory, OrderedDict(subcategory_data))
                for level3 in sub_item.find('{urn:1C.ru:commerceml_3}Группы'):
                    child_category, _ = ChildCategory.objects.get_or_create(
                        external_id=level3.find('{urn:1C.ru:commerceml_3}Ид').text,
                        category=subcategory
                    )
                    child_category_data = {
                        'category': subcategory,
                        **_get_instance_data(level3)
                    }
                    update_object(child_category, OrderedDict(child_category_data))
    os.remove(xml_path)
    ImportStatus.objects.filter(filename=filename).delete()


def get_or_create_import_status(filename):
    return ImportStatus.objects.get_or_create(filename=filename)


def _get_good_main_data(item):
    main_data = {}
    for data in item.find('{urn:1C.ru:commerceml_3}ЗначенияРеквизитов'):
        if data.find('{urn:1C.ru:commerceml_3}Наименование').text == 'Полное наименование':
            main_data['name'] = data.find('{urn:1C.ru:commerceml_3}Значение').text
        if data.find('{urn:1C.ru:commerceml_3}Наименование').text == 'Код':
            main_data['vendor_code'] = data.find('{urn:1C.ru:commerceml_3}Значение').text
    return main_data


def _get_good_data(item):
    return {
        'external_id': item.find('{urn:1C.ru:commerceml_3}Ид').text,
        'version': item.find('{urn:1C.ru:commerceml_3}НомерВерсии').text,
        'barcode': item.find('{urn:1C.ru:commerceml_3}Штрихкод').text,
        'weight': item.find('{urn:1C.ru:commerceml_3}Вес').text,
        'base_unit': item.find('{urn:1C.ru:commerceml_3}БазоваяЕдиница').text,
        **_get_good_main_data(item)
    }


@after_response.enable
def fetch_goods_from_xml(xml_path, filename=''):
    tree = ElementTree.parse(xml_path)
    current = 0
    tree.findall('{urn:1C.ru:commerceml_3}Каталог')
    for node in tree.findall('{urn:1C.ru:commerceml_3}Каталог'):
        current += 1
        inner_current = 0
        for item in node.find('{urn:1C.ru:commerceml_3}Товары'):
            inner_current += 1
            if item.find('{urn:1C.ru:commerceml_3}ПометкаУдаления').text == 'false':
                good, _ = Product.objects.get_or_create(external_id=item.find('{urn:1C.ru:commerceml_3}Ид').text)
                good_data = _get_good_data(item)
                good = update_object(good, OrderedDict(good_data))
                sub_categories = []
                for subcategory in item.findall('{urn:1C.ru:commerceml_3}Группы'):
                    if hasattr(subcategory.find('{urn:1C.ru:commerceml_3}Ид'), 'text'):
                        sub_categories.append(subcategory.find('{urn:1C.ru:commerceml_3}Ид').text)
                subcategories = ChildCategory.objects.filter(external_id__in=sub_categories)
                good.categories.set(subcategories)
                for sub_item in item.find('{urn:1C.ru:commerceml_3}ЗначенияСвойств'):
                    property_name = sub_item.find('{urn:1C.ru:commerceml_3}Ид')
                    value = sub_item.find('{urn:1C.ru:commerceml_3}Значение')
                    if property_name is not None:
                        if value is not None:
                            value = value.text
                        property_name = property_name.text
                        if property_name == 'ОписаниеТовара':
                            good.description = value
                            continue
                        if sub_item.find('{urn:1C.ru:commerceml_3}Ид').text.count(' ') == 0 and \
                                is_camel_case(sub_item.find('{urn:1C.ru:commerceml_3}Ид').text) and \
                                sum(map(str.isupper, sub_item.find('{urn:1C.ru:commerceml_3}Ид').text)) > 1:
                            continue
                        property_obj, _ = Property.objects.get_or_create(
                            name=sub_item.find('{urn:1C.ru:commerceml_3}Ид').text)
                        if value is not None:
                            value, _ = PropertyValue.objects.get_or_create(property=property_obj, value=value)
                        if property_obj.name:
                            if property_obj.name.count(' ') == 0 and is_camel_case(property_obj.name) and \
                                    sum(map(str.isupper, property_obj.name)) > 1:
                                property_obj.is_active = False
                                property_obj.save()
                        product_property, _ = ProductProperty.objects.get_or_create(product=good, property_value=value)
                good.save()
    os.remove(xml_path)
    ImportStatus.objects.filter(filename=filename).delete()


@after_response.enable
def fetch_prices_from_xml(xml_path, filename=''):
    tree = ElementTree.parse(xml_path)
    for node in tree.findall('{urn:1C.ru:commerceml_3}ПакетПредложений'):
        for item in node.find('{urn:1C.ru:commerceml_3}Предложения'):
            good_id = item.find('{urn:1C.ru:commerceml_3}Ид').text
            try:
                product = Product.objects.get(external_id=good_id)
                prices_dict = product.prices_dict

                for price in item.find('{urn:1C.ru:commerceml_3}Цены'):
                    sklad_id = price.find('{urn:1C.ru:commerceml_3}ИдТипаЦены').text
                    storehouse_type = StorehouseTypeChoices.DISCOUNT
                    if 'NOdc' in sklad_id:
                        storehouse_type = StorehouseTypeChoices.BASIC
                    storehouse, _ = Storehouse.objects.get_or_create(external_id=sklad_id,
                                                                     storehouse_type=storehouse_type)
                    product_price, _ = ProductPrice.objects.get_or_create(product=product, storehouse=storehouse)
                    product_price.price = price.find('{urn:1C.ru:commerceml_3}ЦенаЗаЕдиницу').text
                    product_price.save()
                    for city in City.objects.filter(storehouses__id=storehouse.id):
                        prices_dict.update({
                            f"{city.slug}_{storehouse_type}": int(price.find(
                                '{urn:1C.ru:commerceml_3}ЦенаЗаЕдиницу').text)
                        })
                product.prices_dict = prices_dict
                product.save()
            except Product.DoesNotExist:
                continue
    os.remove(xml_path)
    ImportStatus.objects.filter(filename=filename).delete()


@after_response.enable
def fetch_documents_from_xml(xml_path, filename=''):
    tree = ElementTree.parse(xml_path)
    for node in tree.findall('{urn:1C.ru:commerceml_3}Контейнер'):
        for item in node.findall('{urn:1C.ru:commerceml_3}Документ'):
            order_id = item.find('{urn:1C.ru:commerceml_3}Ид').text
            props = item.find('{urn:1C.ru:commerceml_3}ЗначенияРеквизитов')
            order_statuses = list(filter(lambda x: x.find('{urn:1C.ru:commerceml_3}Наименование').text == 'Статус',
                                  props.findall('{urn:1C.ru:commerceml_3}ЗначениеРеквизита')))
            order_status = None
            if len(order_statuses) > 0:
                order_status = order_statuses[0].find('{urn:1C.ru:commerceml_3}Значение').text
            translated_order_status = ORDER_STATUS_TRANSLATES.get(order_status)
            if translated_order_status:
                Order.objects.filter(order_id=order_id).update(status=translated_order_status)
    os.remove(xml_path)
    ImportStatus.objects.filter(filename=filename).delete()


@after_response.enable
def fetch_rests_from_xml(xml_path, filename=''):
    tree = ElementTree.parse(xml_path)
    for node in tree.findall('{urn:1C.ru:commerceml_3}ПакетПредложений'):
        for item in node.find('{urn:1C.ru:commerceml_3}Предложения'):
            good_id = item.find('{urn:1C.ru:commerceml_3}Ид').text
            try:
                product = Product.objects.get(external_id=good_id)
                rests_dict = product.rests_dict
                for rest in item.find('{urn:1C.ru:commerceml_3}Остатки'):
                    sklad = rest.find('{urn:1C.ru:commerceml_3}Склад')
                    sklad_id = sklad.find('{urn:1C.ru:commerceml_3}Ид').text
                    quantity = sklad.find('{urn:1C.ru:commerceml_3}Количество').text
                    if quantity:
                        quantity = int(quantity)
                    else:
                        quantity = 0
                    storehouse_type = StorehouseTypeChoices.DISCOUNT
                    if 'NOdc' in sklad_id:
                        storehouse_type = StorehouseTypeChoices.BASIC
                    storehouse, _ = Storehouse.objects.get_or_create(external_id=sklad_id,
                                                                     storehouse_type=storehouse_type)
                    product_rest, _ = Rest.objects.get_or_create(product=product, storehouse=storehouse)
                    product_rest.quantity = quantity
                    product_rest.save()
                    for city in City.objects.filter(storehouses__id=storehouse.id):
                        rests_dict.update({
                            f"{city.slug}_{storehouse_type}": quantity
                        })
                product.rests_dict = rests_dict
                product.save()
            except Product.DoesNotExist:
                continue
    os.remove(xml_path)
    ImportStatus.objects.filter(filename=filename).delete()
