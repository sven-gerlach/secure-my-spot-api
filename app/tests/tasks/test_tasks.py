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
    def test_unreserve_parking_spot(
        self, send_reservation_has_ended_mail, reservation_unauth_user
    ):
        # extract arguments for unreserve_parking_spot task
        parking_spot_id = reservation_unauth_user.parking_spot.id
        reservation_id = reservation_unauth_user.id

        # call method to be tested
        unreserve_parking_spot(parking_spot_id, reservation_id)

        # retrieve parking spot from db
        reserved_parking_spot = ParkingSpot.objects.get(id=parking_spot_id)

        # assertions
        assert reserved_parking_spot.reserved is False
        assert send_reservation_has_ended_mail.called
