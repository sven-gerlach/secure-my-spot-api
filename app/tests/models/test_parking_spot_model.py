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

    def test_create_valid_parking_spot(self, parking_spot):
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

    def test_utility_method(self, parking_spot):
        """
        This test utilises the pytest recommended approach of using fixtures as arguments of test
        functions. In this case, the fixture parking_spot generates, stores, and returns a parking
        spot model instance.
        """
        assert (
            parking_spot.get_coordinates
            == f"{parking_spot.latitude},{parking_spot.longitude}"
        )
        assert parking_spot.get_status == "available"
        assert (
            str(parking_spot) == f"Parking spot {parking_spot.id}, located at "
            f"({parking_spot.get_coordinates}), "
            f"is {parking_spot.get_status} for an hourly rate of "
            f"{parking_spot.rate}"
        )
        assert parking_spot.get_dictionary("latitude", "longitude", "rate") == {
            "latitude": parking_spot.latitude,
            "longitude": parking_spot.longitude,
            "rate": parking_spot.rate,
        }
