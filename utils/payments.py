"""
Module for payments processing
"""

from app.models.reservation import Reservation


def get_total_reservation_fee(reservation_id):
    """
    Return the total reservation fee based on the reservation duration and the hourly rate,
    formatted to two decimal places
    """

    reservation = Reservation.objects.get(id=reservation_id)
    duration_minutes = reservation.duration
    rate_per_hour = reservation.rate
    return round(duration_minutes * rate_per_hour / 60, 2)
