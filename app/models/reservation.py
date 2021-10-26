"""
A model for reservations.
"""

from django.db import models

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
    user: ensure that deleting a user does not delete the parking spaces which reference the
    deleted user. Instead, foreign key should be set to null (only works if field is null-able).
    """

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
