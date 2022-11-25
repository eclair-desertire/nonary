from datetime import datetime
from xml.etree import ElementTree
from django.apps import apps

Product = apps.get_model(app_label='shop', model_name='Product')
Property = apps.get_model(app_label='shop', model_name='Property')
PropertyValue = apps.get_model(app_label='shop', model_name='PropertyValue')
ProductProperty = apps.get_model(app_label='shop', model_name='ProductProperty')
Brand = apps.get_model(app_label='shop', model_name='Brand')
ProductImage = apps.get_model(app_label='shop', model_name='ProductImage')


def _set_properties(product, offer):
    properties = offer.findall('param')
    for _property in properties:
        property_obj, _ = Property.objects.get_or_create(name=_property.get('name'))
        property_value, _ = PropertyValue.objects.get_or_create(property=property_obj, value=_property.text)
        ProductProperty.objects.get_or_create(product=product, property_value=property_value)


def _set_brand(product, offer):
    brand = offer.find('vendor')
    if brand is not None:
        brand_name = brand.text
        brand, _ = Brand.objects.get_or_create(name=brand_name)
        product.brand = brand
    return product


def _set_images(product, offer):
    image_urls = offer.findall('picture')
    if image_urls is not None:
        secondary_images = []
        if len(image_urls) > 0:
            main_image = list(filter(lambda x: '-1.' in x.text, image_urls))
            if len(main_image) > 0:
                main_image = main_image[0].text
            else:
                main_image = image_urls[0].text
            for img in image_urls:
                if img.text != main_image:
                    secondary_images.append(ProductImage(image=img.text, product=product))
            if len(secondary_images) > 0:
                ProductImage.objects.filter(product=product).delete()
                ProductImage.objects.bulk_create(secondary_images)
            product.image = main_image
    return product


def get_product_images_and_properties_from_website(file_path):

    tree = ElementTree.parse(file_path)

    shop = tree.find('shop')

    offers = shop.find('offers')

    offer_list = offers.findall('offer')
    start = datetime.now()
    print('Started:', start)

    for offer in offer_list:
        vendor_code = offer.find('vendorCode')
        if vendor_code is None:
            continue
        vendor_code = vendor_code.text
        try:
            product = Product.objects.get(vendor_code=vendor_code)
        except Product.DoesNotExist:
            continue
        product = _set_images(product, offer)
        product = _set_brand(product, offer)
        _set_properties(product, offer)
        product.save()
    end = datetime.now()
    print('Finished:', end)
    print('Total seconds:', (end-start).total_seconds())