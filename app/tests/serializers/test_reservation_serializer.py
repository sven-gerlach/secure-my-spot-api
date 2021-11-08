"""
Testing the reservation serializer
"""

from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APIRequestFactory

from app.models.parking_spot import ParkingSpot
from app.models.user import User
from app.serializers.reservation_serializer import ReservationSerializer

pytestmark = pytest.mark.django_db


class TestReservationSerializer:
    """
    Test serializing, deserializing, serializer methods, and validation
    """

    def test_serializing(self, reservation_auth_user):
        """
        Not testing datetime due to difficulties parsing the serialized datetime string
        """
        user = User.objects.get(id=reservation_auth_user.user.id)
        parking_spot = ParkingSpot.objects.get(id=reservation_auth_user.parking_spot.id)

        serializer = ReservationSerializer(reservation_auth_user)
        data = serializer.data

        # assertions
        assert data["user"] == user.id
        assert data["email"] == user.email
        assert data["parking_spot"] == parking_spot.id
        assert Decimal(data["rate"]) == parking_spot.rate
        assert data["paid"] is False

    def test_deserializing(self, reservation_auth_user):
        """
        Not testing datetime due to difficulties parsing the serialized datetime string
        """
        # use the fixture field values as raw inputs into the serializer

        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=10)

        data = {
            "user": reservation_auth_user.user.id,
            "email": reservation_auth_user.email,
            "parking_spot": reservation_auth_user.parking_spot.id,
            "rate": reservation_auth_user.rate,
            "start_time": start_time,
            "end_time": end_time,
        }

        serializer = ReservationSerializer(
            data=data, context={"user": reservation_auth_user.user}
        )

        # assertions
        assert serializer.is_valid() is True
        assert serializer.validated_data["user"] == reservation_auth_user.user
        assert serializer.validated_data["email"] == reservation_auth_user.email
        assert (
            serializer.validated_data["parking_spot"]
            == reservation_auth_user.parking_spot
        )
        assert serializer.validated_data["rate"] == reservation_auth_user.rate

    def test_create_method(self, user, parking_spot):
        # use primary user and parking spot data without there being an existing reservation
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=10)

        data = {
            "user": user.id,
            "email": user.email,
            "parking_spot": parking_spot.id,
            "rate": parking_spot.rate,
            "start_time": start_time,
            "end_time": end_time,
        }

        serializer = ReservationSerializer(data=data, context={"user": user})
        serializer.is_valid()
        reservation = serializer.save()

        # assertions
        assert reservation.email == data["email"]

    def test_update_method(self, reservation_auth_user):
        end_time = datetime.now() + timedelta(minutes=120)

        data = {"paid": True, "end_time": end_time}

        serializer = ReservationSerializer(
            reservation_auth_user, data=data, partial=True
        )
        serializer.is_valid()
        updated_reservation = serializer.save()

        # assertions
        assert updated_reservation.paid is True

    def test_validate_method(self, user, parking_spot):
        """
        end_time <= start_time should throw validation error
        """

        start_time = datetime.now()

        data = {
            "user": user.id,
            "email": user.email,
            "parking_spot": parking_spot.id,
            "rate": parking_spot.rate,
            "start_time": start_time,
            "end_time": start_time,
        }

        serializer = ReservationSerializer(data=data, context={"user": user})

        # assertions
        assert serializer.is_valid() is False

    def test_validate_method_partial_update(self, reservation_auth_user):
        data = {"end_time": reservation_auth_user.start_time}

        serializer = ReservationSerializer(
            reservation_auth_user, data=data, partial=True
        )

        # assertions
        assert serializer.is_valid() is False

    def test_validate_parking_spot_method_unavailable(self, user, parking_spot):
        """
        Commercially unavailable parking spot cannot be reserved
        """

        # render parking spot commercially unavailable
        parking_spot.active = False
        parking_spot.save()

        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=10)

        data = {
            "user": user.id,
            "email": user.email,
            "parking_spot": parking_spot.id,
            "rate": parking_spot.rate,
            "start_time": start_time,
            "end_time": end_time,
        }

        serializer = ReservationSerializer(data=data, context={"user": user})

        # assertions
        assert serializer.is_valid() is False

    def test_validate_parking_spot_method_reserved(self, user, parking_spot):
        """
        Reserved parking spot cannot be reserved
        """

        # render parking spot commercially unavailable
        parking_spot.reserved = True
        parking_spot.save()

        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=10)

        data = {
            "user": user.id,
            "email": user.email,
            "parking_spot": parking_spot.id,
            "rate": parking_spot.rate,
            "start_time": start_time,
            "end_time": end_time,
        }

        serializer = ReservationSerializer(data=data, context={"user": user})

        # assertions
        assert serializer.is_valid() is False

    def test_validate_email_method_existing_account(self, user, parking_spot):
        """
        The usage of an email by an unauthenticated user, attempting to reserve a parking spot,
        when that email is also registered with a user in the database needs to throw a
        ValidationError
        """

        # set valid start- and end-times and create data for serializer
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=10)

        data = {
            "email": user.email,
            "parking_spot": parking_spot.id,
            "rate": parking_spot.rate,
            "start_time": start_time,
            "end_time": end_time,
        }

        # create request mock and set unauthenticated user
        factory = APIRequestFactory()
        path = f"/reservation/{parking_spot.id}/"
        request = factory.post(path, format="json")
        request.user = AnonymousUser()

        serializer = ReservationSerializer(data=data, context={"user": request.user})

        # assertions
        assert serializer.is_valid() is False
