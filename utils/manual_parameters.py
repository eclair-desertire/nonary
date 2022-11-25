from drf_yasg import openapi

from utils.choices import OrderStatusChoices

QUERY_LATITUDE = openapi.Parameter('latitude', openapi.IN_QUERY, type=openapi.TYPE_NUMBER)
QUERY_LONGITUDE = openapi.Parameter('longitude', openapi.IN_QUERY, type=openapi.TYPE_NUMBER)
QUERY_RADIUS = openapi.Parameter('radius', openapi.IN_QUERY, type=openapi.TYPE_NUMBER)
QUERY_CHAT = openapi.Parameter('chat', openapi.IN_QUERY, type=openapi.TYPE_INTEGER)
QUERY_CITY_SLUG = openapi.Parameter('city_slug', openapi.IN_QUERY, type=openapi.TYPE_STRING)
QUERY_FROM_MAP = openapi.Parameter('from_map', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN)
QUERY_ORDERING = openapi.Parameter('ordering', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                                   enum=[
                                       'name', 'discount_price', 'created_at', 'popularity', 'rating',
                                       '-name', '-discount_price', '-created_at', '-popularity', '-rating'
                                   ])

BODY_IMAGE1 = openapi.Parameter('image_1', openapi.IN_BODY, type=openapi.TYPE_FILE, required=False)
BODY_IMAGE2 = openapi.Parameter('image_2', openapi.IN_BODY, type=openapi.TYPE_FILE, required=False)
QUERY_PRODUCT_ID = openapi.Parameter('product', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True,
                                     description='id of current product')
QUERY_COMPILATION = openapi.Parameter('compilation', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False,
                                      description='id of compilations')

QUERY_GEOCODE = openapi.Parameter('geocode', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False,
                                  description='long lat with comma, or address')
PATH_GEOCODE = openapi.Parameter('geocode_type', openapi.IN_PATH, type=openapi.TYPE_STRING, required=True,
                                 description='id of compilations', enum=['coordinates', 'name'])
QUERY_CATEGORY_SLUG = openapi.Parameter('category', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True,
                                        description='id of 2nd category level')
QUERY_ORDER_STATUS = openapi.Parameter('status', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False,
                                       description='Status of orders', enum=OrderStatusChoices.values)