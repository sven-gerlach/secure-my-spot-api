from decimal import Decimal

import pytest

from ..models.parking_spot import ParkingSpot

pytestmark = pytest.mark.django_db


class TestParkingSpotModel:
    """
    A test suite for testing the parking spots model
    """

    def test_create_valid_parking_spot(self):
        parking_spot = ParkingSpot.objects.create(
            latitude=Decimal("10.123456"),
            longitude=Decimal("-170.123456"),
            rate=Decimal("28.17"),
        )

        # retrieve last object from db
        new_parking_spot = ParkingSpot.objects.last()

        assert ParkingSpot.objects.count() == 1
        assert new_parking_spot.latitude == Decimal("10.123456")
        assert new_parking_spot.longitude == Decimal("-170.123456")
        assert new_parking_spot.rate == Decimal("28.17")

    