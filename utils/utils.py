"""
Module contains utility or helper functions
"""
from decimal import Decimal


def is_integer(decimal: Decimal) -> bool:
    """
    Check if decimal is an integer.
    """

    integer = int(decimal)

    delta = integer - decimal

    if delta == 0:
        return True

    return False
