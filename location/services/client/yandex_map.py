import requests
from django.conf import settings
from django.apps import apps


City = apps.get_model(app_label='location', model_name='City')


def _get_from_yandex_api(geocode):
    url = f"https://geocode-maps.yandex.ru/1.x/?apikey={settings.YANDEX_MAP_API_KEY}&geocode={geocode}&format=json"
    response = requests.get(url)
    return response.json(), response.status_code


def _get_key(key):
    if key in ['province', 'locality']:
        return 'city_name'
    return key


def _get_city(filter_lookup):
    return City.objects.get(**filter_lookup)


def _get_city_id_by_name(city_name):
    if city_name:
        city_name = city_name.lower()
    try:
        city = _get_city({'name__icontains': city_name})
        return city.id, city.slug
    except City.DoesNotExist:
        return None, None


def _reformat_address_data(address_data: dict):
    district = address_data.get('district', '')
    street = address_data.get('street', '')
    house = address_data.get('house', '')
    streets = []
    if district:
        streets.append(district)
        address_data.pop('district')

    if house:
        street += f" {house}"
        address_data.pop('house')
        address_data.update({'office': ''})

    if street:
        streets.append(street)
    new_street = ', '.join(streets)
    if new_street:
        address_data.update({
            'street': new_street
        })
        return address_data
    return None


def search_by_coordinates(coordinates, city_slug=None, from_map=False):
    if city_slug and not from_map:
        city = _get_city({'slug': city_slug})
        coordinates = f"{city.name}, {coordinates}"
    data, status_code = _get_from_yandex_api(coordinates)
    response = data.get('response', None)
    if response:
        geo_object_collection = response.get('GeoObjectCollection')
        if geo_object_collection:
            feature_member = geo_object_collection.get('featureMember')
            if feature_member:
                for member in feature_member:
                    geo_object = member.get('GeoObject')
                    if geo_object:
                        meta_data_property = geo_object.get('metaDataProperty')
                        point = geo_object.get('Point')
                        point_data = {}
                        if point:
                            pos = point.get('pos')
                            if pos:
                                pos = pos.split(' ')
                                point_data.update({
                                   'latitude': pos[1],
                                   'longitude': pos[0],
                                })
                        if meta_data_property:
                            geocoder_meta_data = meta_data_property.get('GeocoderMetaData')
                            if geocoder_meta_data:
                                address = geocoder_meta_data.get('Address')
                                if address:
                                    components = address.get('Components', [])
                                    address_data = {_get_key(item.get('kind')): item.get('name') for item in components}
                                    address_data = _reformat_address_data(address_data)
                                    if not address_data:
                                        return None, 404
                                    if not address_data.get('city_name'):
                                        return None, 404
                                    city_id, city_slug_check = _get_city_id_by_name(address_data.get('city_name'))
                                    if not city_id or (city_slug and city_slug_check != city_slug):
                                        return None, 404
                                    return {
                                               **address_data,
                                               **point_data,
                                               'city_id': city_id,
                                               'city_slug': city_slug
                                           }, status_code
    return None, 404

