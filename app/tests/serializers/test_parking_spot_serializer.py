"""
Test the parking spot serializer
"""

from decimal import Decimal

import pytest
from django.test import TestCase

from app.models.parking_spot import ParkingSpot
from app.serializers.parking_spot_serializer import ParkingSpotSerializer

from ..factories import ParkingSpotFactory

pytestmark = pytest.mark.django_db


class TestParkingSpotSerializer(TestCase):
    """
    Test suite for all parking spot serializer tests
    """

    # In Django this method of setting up data inside a classmethod which overrides a method on
    # TestCase is the preferred solution according to Django docs. Pytest suggests to Fixtures
    # which can then be loaded into classes or test methods.
    # https://docs.djangoproject.com/en/3.2/topics/testing/tools/#testcase
    # https://docs.pytest.org/en/6.2.x/fixture.html#fixtures
    @classmethod
    def setUpTestData(cls):
        """
        Create a single serialized parking spot
        """
        # create a new random parking spot from the parking spot factory and save it onto the db
        ParkingSpotFactory.create()

        # retrieve parking spot from db
        parking_spot = ParkingSpot.objects.last()
        serializer = ParkingSpotSerializer(parking_spot)

        cls.parking_spot = parking_spot
        cls.serialized_data = serializer.data

    def test_serialize_parking_spot(self):
        """
        Create a new parking spot with the model object manager and serialize that class instance.
        """

        assert self.serialized_data["lat"] == str(self.parking_spot.lat)
        assert self.serialized_data["lng"] == str(self.parking_spot.lng)
        assert self.serialized_data["rate"] == str(self.parking_spot.rate)
        assert self.serialized_data["reserved"] is False

    def test_deserialize_parking_spot(self):
        """
        The deserialized parking spot should be valid and carry the same data as the db query set
        """

        serializer = ParkingSpotSerializer(data=self.serialized_data)

        # assert that data is valid
        assert serializer.is_valid() is True

        deserialized_data = serializer.validated_data

        # compare all four data points to original data
        assert str(deserialized_data["lat"]) == self.serialized_data["lat"]
        assert str(deserialized_data["lng"]) == self.serialized_data["lng"]
        assert str(deserialized_data["rate"]) == self.serialized_data["rate"]
        assert deserialized_data["reserved"] == self.serialized_data["reserved"]

    def test_deserialize_invalid_lat(self):
        """
        Change latitude in serialized_data to test upper and lower bounds as well as the limit of 6
        decimals.
        """

        # # create shallow copies of the serialized data dictionary
        invalid_upper_bound = ParkingSpotFactory.build(lat=Decimal("91"))
        invalid_lower_bound = ParkingSpotFactory.build(lat=Decimal("-91"))
        invalid_decimals = ParkingSpotFactory.build(lat=Decimal("0.0000001"))

        # create serializers
        serializer_invalid_upper_bound = ParkingSpotSerializer(
            data=invalid_upper_bound.get_dictionary("lat", "lng", "rate")
        )
        serializer_invalid_lower_bound = ParkingSpotSerializer(
            data=invalid_lower_bound.get_dictionary("lat", "lng", "rate")
        )
        serializer_invalid_decimals = ParkingSpotSerializer(
            data=invalid_decimals.get_dictionary("lat", "lng", "rate")
        )

        # assertions
        assert serializer_invalid_upper_bound.is_valid() is False
        assert serializer_invalid_lower_bound.is_valid() is False
        assert serializer_invalid_decimals.is_valid() is False

    def test_deserialize_invalid_lng(self):
        """
        Change longitude in serialized_data to test upper and lower bounds as well as the limit of 6
        decimals.
        """

        # # create shallow copies of the serialized data dictionary
        invalid_upper_bound = ParkingSpotFactory.build(lng=Decimal("181"))
        invalid_lower_bound = ParkingSpotFactory.build(lng=Decimal("-180"))
        invalid_decimals = ParkingSpotFactory.build(lng=Decimal("0.0000001"))

        # create serializers
        serializer_invalid_upper_bound = ParkingSpotSerializer(
            data=invalid_upper_bound.get_dictionary("lat", "lng", "rate")
        )
        serializer_invalid_lower_bound = ParkingSpotSerializer(
            data=invalid_lower_bound.get_dictionary("lat", "lng", "rate")
        )
        serializer_invalid_decimals = ParkingSpotSerializer(
            data=invalid_decimals.get_dictionary("lat", "lng", "rate")
        )

        # assertions
        assert serializer_invalid_upper_bound.is_valid() is False
        assert serializer_invalid_lower_bound.is_valid() is False
        assert serializer_invalid_decimals.is_valid() is False

    def test_deserialize_invalid_rate(self):
        """
        Change rate in serialized_data to test lower bound as well as the limit of 2
        decimals.
        """

        # # create shallow copies of the serialized data dictionary
        invalid_lower_bound = ParkingSpotFactory.build(rate=Decimal("-0.01"))
        invalid_decimals = ParkingSpotFactory.build(rate=Decimal("0.001"))

        # create serializers
        serializer_invalid_lower_bound = ParkingSpotSerializer(
            data=invalid_lower_bound.get_dictionary("lat", "lng", "rate")
        )
        serializer_invalid_decimals = ParkingSpotSerializer(
            data=invalid_decimals.get_dictionary("lat", "lng", "rate")
        )

        # assertions
        assert serializer_invalid_lower_bound.is_valid() is False
        assert serializer_invalid_decimals.is_valid() is False
