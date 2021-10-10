"""
Module contains utility or helper functions
"""
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
