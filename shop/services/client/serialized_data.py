
def _get_property_key(item, is_multiple):
    return f"{item.property_value.property.name}_{item.property_value.property.property_type}_{is_multiple}"


def _get_real_value(is_multiple, property_value):
    if is_multiple and property_value.hex_value:
        return property_value.hex_value
    return property_value.value


def get_properties(instance, properties, similar_properties, images_serializer):
    if hasattr(instance, 'property_list'):
        for item in instance.property_list:
            is_multiple = item.property_value.property_id in similar_properties
            real_value = _get_real_value(is_multiple, item.property_value)
            if _get_property_key(item, is_multiple) in properties:
                values = properties[_get_property_key(item, is_multiple)]
                if real_value in values:
                    value = values.get(real_value, {})
                    products = value.get('products', [])
                    products.append({
                        'product_id': instance.id,
                        'description': instance.description,
                        'rest': instance.rest,
                        'price': instance.price,
                        'discount_price': instance.discount_price,
                        'product_name': instance.name,
                        'slug': instance.slug,
                        'image': instance.image,
                        'images': images_serializer(instance.images.all(), many=True).data
                    })
                    value.update({'products': products})
                    properties[_get_property_key(item, is_multiple)]\
                        .update({real_value: value})
                else:
                    products = [{
                        'product_id': instance.id,
                        'description': instance.description,
                        'rest': instance.rest,
                        'price': instance.price,
                        'discount_price': instance.discount_price,
                        'product_name': instance.name,
                        'slug': instance.slug,
                        'image': instance.image,
                        'images': images_serializer(instance.images.all(), many=True).data
                    }]
                    properties[_get_property_key(item, is_multiple)]\
                        .update({real_value: {'value': real_value, 'products': products}})
            else:
                item_values = {
                    real_value: {
                        'value': real_value,
                        'products': [{
                            'product_id': instance.id,
                            'description': instance.description,
                            'rest': instance.rest,
                            'price': instance.price,
                            'discount_price': instance.discount_price,
                            'product_name': instance.name,
                            'slug': instance.slug,
                            'image': instance.image,
                            'images': images_serializer(instance.images.all(), many=True).data
                        }]
                    }
                }
                properties.update({
                    _get_property_key(item, is_multiple): item_values
                })
    return properties


def _reformat_values(value):
    return [v for _, v in value.items()]


def _get_property_data(key):
    keys = key.split('_')
    return {
        'name': keys[0],
        'property_type': keys[1],
        'is_selectable': keys[2] == 'True',
    }


def reformat_properties(properties):
    return [{**_get_property_data(key), 'values': _reformat_values(value)} for key, value in properties.items()]
