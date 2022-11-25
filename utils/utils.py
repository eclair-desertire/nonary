from abc import ABCMeta

from django.db.models import Func
from django.db.models.functions import math

EARTH_RADIUS_IN_MILES = 6371


class Radians(Func, metaclass=ABCMeta):
    function = 'RADIANS'


class Sin(Func, metaclass=ABCMeta):
    function = 'SIN'


class Cos(Func, metaclass=ABCMeta):
    function = 'COS'


class Acos(Func, metaclass=ABCMeta):
    function = 'ACOS'


def get_distance(lat1, lon1, lat2, lon2):
    lat1 = Radians(lat1)
    lat2 = Radians(lat2)

    delta_lon = Radians(lon1) - Radians(lon2)

    # Distance formula
    cos_x = (math.Sin(lat1) * math.Sin(lat2) + math.Cos(lat1) * math.Cos(lat2) * math.Cos(delta_lon))

    # Conversion to miles
    distance = math.ACos(cos_x) * EARTH_RADIUS_IN_MILES
    return distance


def is_camel_case(s):
    return s != s.lower() and s != s.upper() and "_" not in s
