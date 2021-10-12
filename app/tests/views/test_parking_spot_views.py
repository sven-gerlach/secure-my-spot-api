import pytest
from django.test import Client
import json

pytestmark = pytest.mark.django_db


class TestParkingSpotViews():
    """
    A test suite for all parking spot views
    """

    def test_get_all_parking_spots_view(self, parking_spots):
        c = Client()
        response = c.get("/available-parking-spots/")

        # destruct the parking spots list into a dictionary with key / value pairs containing
        # latitude, longitude, rate, reserved, created_at, and updated_at

        # Note: created_at and updated_at are removed because the date/time formatting difference
        decoded_response = json.loads(response.content)
        for _ in decoded_response:
            del _["created_at"]
            del _["updated_at"]

        parking_spots_list = [
            {
                "latitude": f"{parking_spot.latitude}",
                "longitude": f"{parking_spot.longitude}",
                "rate": f"{parking_spot.rate}",
                "reserved": parking_spot.reserved
            } for parking_spot in parking_spots
        ]

        # Assertions
        assert response.status_code == 200
        assert decoded_response == parking_spots_list
