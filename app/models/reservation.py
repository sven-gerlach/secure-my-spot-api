"""
A model for reservations.
"""

from django.db import models

from .parking_spot import ParkingSpot
from .user import User


class Reservation(models.Model):
    """
    A model that represents a reservation.

    This resource needs to comply with two use cases where the user may or may not be
    authenticated.

    For the authenticated case, the model needs to have a foreign key linking this
    resource to the user object as well as a foreign key linking the reservation to the reserved
    parking spot.

    For the unauthenticated case, the model can ONLY reference the parking spot as there is no
    user object to reference. Instead, in the most basic form, the model needs to accept the user's
    email address.

    Class attributes / database fields:
    -----------------------------------
    user: ensure that deleting a user does not delete the reservations which reference the
    deleted user. Instead, foreign key should be set to null (only works if field is null-able).

    email: for unauthenticated users this field stores their email address; in the case of an
    authenticated user this field will be blank

    parking_spot: ensure that parking spots that have a reservation history cannot be deleted

    paid: Record whether the parking spot reservation has been paid for. Note that eventually,
    at the time of creating a new reservation, the payment intent, including payment details,
    will have been collected from the user but the final payment for the parking spot will be
    collected when the reservation period is over. That event could happen before, at or indeed
    after the originally desired end_time

    start_time: record the start time of the reservation

    end_time: record the end time of the reservation
    """

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    email = models.EmailField(blank=True)
    parking_spot = models.ForeignKey(ParkingSpot, on_delete=models.PROTECT)
    paid = models.BooleanField(default=False)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        """
        Return a string representation of the Reservation instance
        """

        parking_spot_id = self.parking_spot.id
        user_id = ""
        if self.user:
            user_id = self.user.id
        else:
            user_id = self.email
        expiration_time = "{:02d}:{:02d}:{:02d}".format(
            self.end_time.hour, self.end_time.minute, self.end_time.second
        )

        return (
            f"This parking reservation with id {parking_spot_id}, associated with user "
            f"{user_id}, expires at {expiration_time}"
        )
