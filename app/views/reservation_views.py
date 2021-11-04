"""
Module for all reservation views
"""
import datetime

from django.contrib.auth import get_user
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.send_mail import send_reservation_confirmation_mail

from ..models.parking_spot import ParkingSpot
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
            data["email"] = get_user(request).email
        else:
            # if the user is not authenticated the user email needs to be provided instead
            data["email"] = request.data["reservation"]["email"]

        # serialize the data stream
        serializer = ReservationSerializer(data=data)

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
            countdown=float(reservation_duration * 20),
        )

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
