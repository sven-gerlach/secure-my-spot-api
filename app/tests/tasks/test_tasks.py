"""
Testing Celery tasks
"""

from unittest.mock import patch

import pytest

from app.models.parking_spot import ParkingSpot
from app.tasks.tasks import unreserve_parking_spot

pytestmark = pytest.mark.django_db


class TestTasks:
    @patch("app.tasks.tasks.send_reservation_has_ended_mail")
    @patch("app.tasks.tasks.charge_customer")
    def test_unreserve_parking_spot(
        self, charge_customer, send_reservation_has_ended_mail, reservation_unauth
    ):
        # extract arguments for unreserve_parking_spot task
        parking_spot_id = reservation_unauth.parking_spot.id
        reservation_id = reservation_unauth.id

        # set parking spot reserved field to true
        parking_spot = ParkingSpot.objects.get(id=parking_spot_id)
        parking_spot.reserved = True
        parking_spot.save()

        # call method to be tested
        unreserve_parking_spot(parking_spot_id, reservation_id)

        # retrieve parking spot from db
        reserved_parking_spot = ParkingSpot.objects.get(id=parking_spot_id)

        # assertions
        assert reserved_parking_spot.reserved is False
        assert send_reservation_has_ended_mail.called
