import json

import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from ..factories import ParkingSpotFactory

pytestmark = pytest.mark.django_db


class TestParkingSpotViews(TestCase):
    """
    A test suite for all parking spot views
    """

    @classmethod
    def setUpTestData(cls):
        # set up client
        cls.client = APIClient()

    def test_get_available_parking_spots_view(self):
        factory = [ParkingSpotFactory() for _ in range(1, 5)]
        view_response = self.client.get(reverse("api-available-parking-spots"))

        # Note: created_at and updated_at are removed because the date/time formatting difference
        decoded_response = json.loads(view_response.content)
        for _ in decoded_response:
            del _["created_at"]
            del _["updated_at"]

        # it is necessary to force python not to truncate decimal zeros, hence the string
        # formatting of lat, long, and rate
        parking_spots_list = [
            {
                "latitude": f"{parking_spot.latitude:.6f}",
                "longitude": f"{parking_spot.longitude:.6f}",
                "rate": f"{parking_spot.rate:.2f}",
                "reserved": parking_spot.reserved,
            }
            for parking_spot in factory
        ]

        # Assertions
        assert view_response.status_code == 200
        assert decoded_response == parking_spots_list

    def test_get_available_parking_spots_view_none_available(self):
        # no parking spots are created and make a get request to the end-point
        view_response = self.client.get(reverse("api-available-parking-spots"))

        # decode JSON bytes response
        decoded_response = json.loads(view_response.content)

        # assertions
        assert view_response.status_code == 200
        assert decoded_response == []
