"""
Testing reservation views
"""

import pytest

from app.models.reservation import Reservation

pytestmark = pytest.mark.django_db


class TestReservationViews:
    """
    Testing reservation views
    """

    def test_create_reservation_view_unauth_user(self, client, parking_spot):
        path = f"/reservation-unauth/{parking_spot.id}/"
        data = {"reservation": {"reservation_length": 10, "email": "test@test.com"}}

        response = client.post(path=path, data=data, format="json")

        reservation = Reservation.objects.last()

        # assertions
        assert response.status_code == 200
        assert reservation.email == data["reservation"]["email"]

    def test_create_reservation_view_auth_user(self, client, parking_spot, user):
        # force authenticate user
        client.force_authenticate(user=user)

        path = f"/reservation-auth/{parking_spot.id}/"
        data = {"reservation": {"reservation_length": 10}}

        response = client.post(path=path, data=data, format="json")

        reservation = Reservation.objects.last()

        # assertions
        assert response.status_code == 200
        assert reservation.email == user.email
