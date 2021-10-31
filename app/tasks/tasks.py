"""
Module for tasks associated with the reservation view
"""


from celery import shared_task
from django.shortcuts import get_object_or_404

from ..models.parking_spot import ParkingSpot


@shared_task
def make_parking_spot_available(parking_spot_id):
    """Makes the parking available for renting again after a reservation has rendered it
    unavailable. This will be achieved by retrieving the parking spot with id from database,
    and then set its field name "reserved" to false

    Params
    ------
    parking_spot_id: the primary key of the parking_spot_instance which ought to be made
    available again
    """
    parking_spot = get_object_or_404(ParkingSpot, id=parking_spot_id)
    parking_spot.reserved = False
    parking_spot.save()
