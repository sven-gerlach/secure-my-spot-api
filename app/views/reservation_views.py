"""
Module for all reservation views
"""

# import Python modules
import datetime

# import Django / RestFramework modules
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.send_mail import send_reservation_confirmation_mail

# import custom modules
from ..models.parking_spot import ParkingSpot
from ..models.reservation import Reservation
from ..serializers.reservation_serializer import ReservationSerializer
from ..tasks.tasks import unreserve_parking_spot


class ReservationViewAuth(APIView):
    """
    API view for creating a new reservation, retrieving all open reservations and changing a
    reservation.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, parking_spot_id):
        """
        Create a new reservation resource associated with an authenticated user and a parking spot.
        """

        # create the data object that needs to be serialized
        data = {}
        rate = ParkingSpot.objects.get(id=parking_spot_id).rate
        time_now = datetime.datetime.now()
        reservation_duration = int(request.data["reservation"]["reservation_length"])
        time_delta = datetime.timedelta(minutes=reservation_duration)
        # storing the user's email on the reservation makes sending notification emails easier
        data = {
            "user": request.user.id,
            "email": request.user.email,
            "parking_spot": parking_spot_id,
            "rate": rate,
            "start_time": time_now,
            "end_time": time_now + time_delta,
        }

        # serialize the data stream
        serializer = ReservationSerializer(data=data, context={"user": request.user})

        # throw a validation exception and send a response if validation fails
        serializer.is_valid(raise_exception=True)

        # otherwise save the new reservation
        serializer.save()

        # and set the related parking spot status to reserved=true
        parking_spot = get_object_or_404(ParkingSpot, id=parking_spot_id)
        parking_spot.reserved = True
        parking_spot.save()

        # set a task that makes the same parking spot available for reservation again after the
        # reservation length is up
        unreserve_parking_spot.apply_async(
            args=[parking_spot_id, serializer.data["id"]],
            countdown=float(reservation_duration * 60),
        )

        # todo: queue a task which sends an email 5min prior to the expiry of the reservation,
        #  providing the user with a link which allows them to extend the reservation

        # declare the response variable such that the email or user key can be removed before
        # sending a JSON response
        response = serializer.data

        # send confirmation email to user
        # pass datetime format instead of stringified time from response object
        send_reservation_confirmation_mail(
            user_mail_address=response["email"],
            parking_spot_id=response["parking_spot"],
            rate=rate,
            reservation_id=response["id"],
            start_time=data["start_time"],
            end_time=data["end_time"],
        )

        # send the response
        return Response(data=response)

    def get(self, request):
        """
        Retrieve all active reservations owned by authenticated user and return the serialized
        result
        """

        active_reservations = Reservation.objects.filter(paid=False, user=request.user)
        serializer = ReservationSerializer(active_reservations, many=True)
        return Response(serializer.data)


class ReservationViewUnauth(APIView):
    """
    API view for creating a new reservation, retrieving a specific reservation and changing a
    specific reservation.
    """

    def post(self, request, parking_spot_id):
        """
        Create a new reservation resource associated with an unauthenticated user's email and a
        parking spot
        """

        # create the data object that needs to be serialized
        data = {}
        rate = ParkingSpot.objects.get(id=parking_spot_id).rate
        time_now = datetime.datetime.now()
        reservation_duration = int(request.data["reservation"]["reservation_length"])
        time_delta = datetime.timedelta(minutes=reservation_duration)
        data = {
            "email": request.data["reservation"]["email"],
            "parking_spot": parking_spot_id,
            "rate": rate,
            "start_time": time_now,
            "end_time": time_now + time_delta,
        }

        # serialize the data stream
        serializer = ReservationSerializer(data=data, context={"user": request.user})

        # throw a validation exception and send a response if validation fails
        serializer.is_valid(raise_exception=True)

        # otherwise save the new reservation
        serializer.save()

        # and set the related parking spot status to reserved=true
        parking_spot = get_object_or_404(ParkingSpot, id=parking_spot_id)
        parking_spot.reserved = True
        parking_spot.save()

        # set a task that makes the same parking spot available for reservation again after the
        # reservation length is up
        unreserve_parking_spot.apply_async(
            args=[parking_spot_id, serializer.data["id"]],
            countdown=float(reservation_duration * 60),
        )

        # todo: queue a task which sends an email 5min prior to the expiry of the reservation,
        #  providing the user with a link which allows them to extend the reservation

        # declare the response variable such that the email or user key can be removed before
        # sending a JSON response
        response = serializer.data

        # send confirmation email to user
        # pass datetime format instead of stringified time from response object
        send_reservation_confirmation_mail(
            user_mail_address=response["email"],
            parking_spot_id=response["parking_spot"],
            rate=rate,
            reservation_id=response["id"],
            start_time=data["start_time"],
            end_time=data["end_time"],
        )

        # send the response
        return Response(data=response)

    def get(self, request, reservation_id, email):
        """
        Retrieve the reservation with id of reservation_id, check that the user is not
        authenticated and that the email matches with the email param. Serialize the reservation
        and return it to the client.
        """

        # get the reservation that matches the provided id and email
        reservation = get_object_or_404(Reservation, id=reservation_id, email=email)

        # if the reservation was made by an authenticated user reject the request
        if reservation.user:
            return Response(
                {
                    "detail": "This reservation belongs to an authenticated account. "
                    "Please login to review this reservation."
                },
                status=401,
            )

        # serialize the data
        serializer = ReservationSerializer(reservation)

        # send the response
        return Response(serializer.data, status=200)


class GetExpiredReservationsAuth(APIView):
    """
    Class provides a list with all expired reservations associated with the authenticated user
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve all expired reservations owned by authenticated user and return the serialized
        result
        """

        expired_reservations = Reservation.objects.filter(paid=True, user=request.user)
        serializer = ReservationSerializer(expired_reservations, many=True)
        return Response(serializer.data)
