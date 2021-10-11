"""
Test the parking spot serializer
"""

import pytest
from app.models.parking_spot import ParkingSpot
from ..factories import ParkingSpotFactory
from app.serializers.parking_spot_serializer import ParkingSpotSerializer
from django.test import TestCase
from copy import copy

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

        assert self.serialized_data["latitude"] == str(self.parking_spot.latitude)
        assert self.serialized_data["longitude"] == str(self.parking_spot.longitude)
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
        assert str(deserialized_data["latitude"]) == self.serialized_data["latitude"]
        assert str(deserialized_data["longitude"]) == self.serialized_data["longitude"]
        assert str(deserialized_data["rate"]) == self.serialized_data["rate"]
        assert deserialized_data["reserved"] == self.serialized_data["reserved"]

    def test_deserialize_invalid_latitude(self):
        """
        Change latitude in serialized_data to test upper and lower bounds as well as the limit of 6
        decimals.
        """

        # create shallow copies of the serialized data dictionary
        invalid_upper_bound = copy(self.serialized_data)
        invalid_lower_bound = copy(self.serialized_data)
        invalid_decimals = copy(self.serialized_data)

        # manipulate all three copies
        invalid_upper_bound["latitude"] = "91"
        invalid_lower_bound["latitude"] = "-91"
        invalid_decimals["latitude"] = "0.0000001"

        # create serializers
        serializer_invalid_upper_bound = ParkingSpotSerializer(data=invalid_upper_bound)
        serializer_invalid_lower_bound = ParkingSpotSerializer(data=invalid_lower_bound)
        serializer_invalid_decimals = ParkingSpotSerializer(data=invalid_decimals)

        print(vars(serializer_invalid_upper_bound), "\n")
        print(vars(serializer_invalid_lower_bound), "\n")
        print(vars(serializer_invalid_decimals), "\n")

        # assertions
        assert serializer_invalid_upper_bound.is_valid() is False
        assert serializer_invalid_lower_bound.is_valid() is False
        assert serializer_invalid_decimals.is_valid() is False
