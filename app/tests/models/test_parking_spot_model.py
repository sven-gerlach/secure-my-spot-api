import copy
from decimal import Decimal

import pytest

from app.models.parking_spot import ParkingSpot
from app.tests.factories import ParkingSpotFactory

pytestmark = pytest.mark.django_db


class TestParkingSpotModel:
    """
    A test suite for testing the parking spots model
    """

    def test_create_valid_parking_spot(self):
        parking_spot = ParkingSpotFactory.create()
        print("latitude: ", parking_spot.latitude)
        print("longitude: ", parking_spot.longitude)
        print("rate: ", parking_spot.rate)

        # retrieve last object from db
        new_parking_spot = ParkingSpot.objects.last()

        assert ParkingSpot.objects.count() == 1
        assert new_parking_spot.latitude == parking_spot.latitude
        assert new_parking_spot.longitude == parking_spot.longitude
        assert new_parking_spot.rate == parking_spot.rate

    def test_create_parking_spot_invalid_latitude(self):
        """
        This test demonstrates that there is no validation at the level of the ParkingSpot model.
        See test suite for ParkingSpotSerializer
        """
        # appropriate parking_spot instance
        parking_spot = ParkingSpotFactory.build()

        # upper bound conflict
        parking_spot_upper_bound_breach = copy.deepcopy(parking_spot)
        parking_spot_upper_bound_breach.latitude = Decimal("91")
        parking_spot_upper_bound_breach.save()

        # lower bound conflict
        parking_spot_lower_bound_breach = copy.deepcopy(parking_spot)
        parking_spot_lower_bound_breach.latitude = Decimal("-91")
        parking_spot_lower_bound_breach.save()

        # decimal conflict
        parking_spot_decimal_breach = copy.deepcopy(parking_spot)
        parking_spot_decimal_breach.latitude = Decimal("0.0000001")
        parking_spot_decimal_breach.save()

        assert ParkingSpot.objects.count() == 3
