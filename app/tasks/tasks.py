"""
Module for tasks associated with the reservation view
"""


from celery import shared_task
from django.shortcuts import get_object_or_404

from utils.send_mail import send_reservation_has_ended_mail

from ..models.parking_spot import ParkingSpot


@shared_task
def unreserve_parking_spot(parking_spot_id, reservation_id):
    """Makes the parking spot available for renting again after a reservation has rendered it
    unavailable. This will be achieved by retrieving the parking spot with id from database,
    and then set its field name "reserved" to false.

    Also, send email to user confirming that their reservation period has ended.

    Params
    ------
    parking_spot_id: the primary key of the parking_spot_instance which ought to be made
    available again
    """

    # make parking spot available for reserving
    parking_spot = get_object_or_404(ParkingSpot, id=parking_spot_id)
    parking_spot.reserved = False
    parking_spot.save()

    # send email to user confirming end of the reservation period
    send_reservation_has_ended_mail(reservation_id)
