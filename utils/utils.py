"""
Module contains utility or helper functions
"""
import math
from decimal import Decimal
from random import uniform
from .ErrorClasses import ValidationError


def is_integer(decimal: Decimal) -> bool:
    """
    Check if decimal is an integer.
    """

    integer = int(decimal)

    delta = integer - decimal

    if delta == 0:
        return True

    return False


def get_rand_decimal(min: float, max: float, right_digits: int) -> Decimal:
    """
    Return a randomly generated Decimal with inclusive upper / lower bounds and decimal precision
    """
    if type(min) is not float and type(min) is not int:
        raise ValidationError("min argument must be either a float or an integer")
    if type(max) is not float and type(max) is not int:
        raise ValidationError("max argument must be either a float or an integer")
    if type(right_digits) is not int:
        raise ValidationError("right_digits must be an integer")
    if max <= min:
        raise ValidationError("max must be strictly larger than min")

    rand_float = uniform(min, max)
    rand_float_rounded = round(rand_float, right_digits)
    rand_str = str(rand_float_rounded)
    return Decimal(rand_str)


def haversine_distance(
        user_latitude: float,
        user_longitude: float,
        parking_spot_latitude: float,
        parking_spot_longitude: float,
        unit: str
) -> float:
    """
    Calculate and return the distance between two GPS coordinates based on the "haversine" formula.
    Source: http://www.movable-type.co.uk/scripts/latlong.html
    """

    # https://en.wikipedia.org/wiki/United_States_customary_units
    conversion_factor = 1 if unit == "km" else 1 / 1.609344

    # mean radius of the Earth (this is sufficiently accurate) in [unit]
    radius_earth = 6371 * conversion_factor

    # convert to radian
    user_latitude_rad = user_latitude * math.pi / 180
    parking_spot_latitude_rad = parking_spot_latitude * math.pi / 180

    # convert lat and long deltas to radian
    latitude_delta_rad = (parking_spot_latitude - user_latitude) * math.pi / 180
    longitude_delta_rad = (parking_spot_longitude - user_longitude) * math.pi / 180

    a = \
        math.sin(latitude_delta_rad / 2) * math.sin(latitude_delta_rad / 2) + \
        math.cos(user_latitude_rad) * math.cos(parking_spot_latitude_rad) * \
        math.sin(longitude_delta_rad / 2) * math.sin(longitude_delta_rad / 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return radius_earth * c
