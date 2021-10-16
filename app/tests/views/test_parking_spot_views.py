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
        for parking_spot in decoded_response:
            del parking_spot["created_at"]
            del parking_spot["updated_at"]
            del parking_spot["id"]

        # it is necessary to force python not to truncate decimal zeros, hence the string
        # formatting of lat, long, and rate
        parking_spots_list = [
            {
                "lat": f"{parking_spot.lat:.6f}",
                "lng": f"{parking_spot.lng:.6f}",
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

    def test_get_available_parking_spots_filtered_view(self):
        # create three parking spots at the null meridian and latitude 0, 1, and 2 deg
        # the step-distance between each incremental degree of latitude is ~111km
        # see http://www.csgnetwork.com/degreelenllavcalc.html
        [ParkingSpotFactory.create(lat=0 + i, lng=0) for i in range(0, 3)]

        # store all 3 response objects in this list
        response_list = []

        # km length of 1 deg in latitude at the equator
        dist = 111

        # create the response object
        for i in range(0, 3):
            response_list.append(
                self.client.get(
                    reverse("api-available-parking-spots-filter")
                    + f"?lat=0&lng=0&unit=km&dist={1 + i * dist}"
                )
            )

        # assertions
        for i in range(0, 3):
            assert response_list[i].status_code == 200
            assert len(json.loads(response_list[i].content)) == 1 + i
