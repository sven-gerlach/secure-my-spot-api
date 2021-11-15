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


class CreateReservationView(APIView):
    """
    Create a new reservation. If the user is not authenticated confirm that data includes the
    user's email and the reservation length (minutes) and the param includes the parking spot id
    """

    def post(self, request, parking_spot_id):
        """
        Post method is split between authenticated and unauthenticated users. In both cases,
        this method invokes data serialization and creates a new reservation resource.
        """

        print(dir(request))
        print(request.user)
        print(dir(request.user))

        # create the data object that needs to be serialized
        data = {}
        rate = ParkingSpot.objects.get(id=parking_spot_id).rate
        time_now = datetime.datetime.now()
        reservation_duration = int(request.data["reservation"]["reservation_length"])
        time_delta = datetime.timedelta(minutes=reservation_duration)
        data = {
            "parking_spot": parking_spot_id,
            "rate": rate,
            "start_time": time_now,
            "end_time": time_now + time_delta,
        }

        # depending on whether the user is authenticated or not either add the user id as a ref
        # key or the provided user email address as a string key to the data object
        if request.user.is_authenticated:
            # if user is authenticated the user id needs to be added to the data dict that will
            # be serialized
            print("================= ", request.user.id, " =================")
            data["user"] = request.user.id
            data["email"] = request.user.email
        else:
            # if the user is not authenticated the user email needs to be provided instead
            data["email"] = request.data["reservation"]["email"]

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

        # Since the serializer is independent of whether the user is authenticated or not,
        # the following code deletes either the email key or the user key from the response object
        if request.user.is_authenticated:
            del response["email"]
            return Response(data=response)
        else:
            del response["user"]
            return Response(data=response)


class GetReservationView(APIView):
    """
    Return a reservation with a specific reservation_id, provided the user is not authenticated
    and the provided email string matches with the email field on the reservation with the id of
    reservation_id
    """

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


class GetActiveReservations(APIView):
    """
    Class provides a list with all active reservations for an authenticated user
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve all active reservations owned by authenticated user and return the serialized
        result
        """
        active_reservations = Reservation.objects.filter(paid=False, user=request.user)
        serializer = ReservationSerializer(active_reservations, many=True)
        return Response(serializer.data)


class GetExpiredReservations(APIView):
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
