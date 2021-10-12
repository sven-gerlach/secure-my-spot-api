import json

import pytest
from django.test import Client

pytestmark = pytest.mark.django_db


class TestParkingSpotViews:
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

        # it is necessary to force python not to truncate decimal zeros, hence the string
        # formatting of lat, long, and rate
        parking_spots_list = [
            {
                "latitude": f"{parking_spot.latitude:.6f}",
                "longitude": f"{parking_spot.longitude:.6f}",
                "rate": f"{parking_spot.rate:.2f}",
                "reserved": parking_spot.reserved,
            }
            for parking_spot in parking_spots
        ]

        # Assertions
        assert response.status_code == 200
        assert decoded_response == parking_spots_list
