"""
Module for tasks associated with the reservation view
"""


from celery import shared_task
from django.shortcuts import get_object_or_404

from utils.payments import charge_customer
from utils.send_mail import send_reservation_has_ended_mail

from ..models import Reservation
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
    reservation = get_object_or_404(Reservation, id=reservation_id)

    # only execute this task if the parking spot is still reserved and if it is not yet paid
    # both are necessary only because task.revoke() does not work in the deployed app on Heroku
    # 2nd condition is needed as it is conceivable that a long-running task in the queue executes
    # at a time when the same parking spot is already being reserved by another customer
    if parking_spot.reserved and not reservation.paid:
        # charge the customer
        charge_customer(reservation_id)

        # make parking spot available for future reservations
        parking_spot.reserved = False
        parking_spot.save()

        # send email to user confirming end of the reservation period
        send_reservation_has_ended_mail(reservation_id)
