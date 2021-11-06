"""
Testing the reservation model
"""

import pprint

import pytest
from django.db.models import ProtectedError

from app.models.parking_spot import ParkingSpot
from app.models.reservation import Reservation
from app.models.user import User

pytestmark = pytest.mark.django_db
pp = pprint.PrettyPrinter(indent=4)


class TestParkingSpotModel:
    """
    A test suite for testing the reservation model
    """

    def test_create_valid_reservation_unauth_user(self, reservation_unauth_user):
        # assertions
        assert Reservation.objects.count() == 1
        assert ParkingSpot.objects.count() == 1
        assert User.objects.count() == 0

    def test_create_valid_reservation_auth_user(self, reservation_auth_user):

        # assertions
        assert Reservation.objects.count() == 1
        assert ParkingSpot.objects.count() == 1
        assert User.objects.count() == 1

    def test_delete_foreign_key_user(self, reservation_auth_user):
        # delete the user instance
        user = User.objects.get(id=reservation_auth_user.user.id)
        user.delete()

        reservation = Reservation.objects.get(id=reservation_auth_user.id)

        # assertions
        assert reservation.user is None

    def test_delete_foreign_key_parking_spot(self, reservation_unauth_user):
        # delete the parking spot instance
        parking_spot = ParkingSpot.objects.get(
            id=reservation_unauth_user.parking_spot.id
        )

        with pytest.raises(ProtectedError):
            parking_spot.delete()

    def test_method__str__(self, reservation_unauth_user):
        expiration_time = "{:02d}:{:02d}:{:02d}".format(
            reservation_unauth_user.end_time.hour,
            reservation_unauth_user.end_time.minute,
            reservation_unauth_user.end_time.second,
        )

        # assertions
        assert (
            reservation_unauth_user.__str__()
            == f"Reservation {reservation_unauth_user.id} for parking spot "
            f"{reservation_unauth_user.parking_spot.id}, associated with user "
            f"{reservation_unauth_user.email}, expires at {expiration_time}"
        )

    def test_method_duration(self, reservation_unauth_user):
        assert reservation_unauth_user.duration == 10
