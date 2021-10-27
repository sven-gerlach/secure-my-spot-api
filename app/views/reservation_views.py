"""
Module for all reservation views
"""
import datetime

from rest_framework.response import Response
from rest_framework.views import APIView

from ..models.parking_spot import ParkingSpot
from ..serializers.reservation_serializer import ReservationSerializer


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

        # todo: add a task scheduler to send out email / text to users 5min prior to their
        #  reservation expiring (e.g. Celery)

        data = {}

        time_now = datetime.datetime.now()
        reservation_duration = int(request.data["reservation"]["reservation_length"])
        time_delta = datetime.timedelta(minutes=reservation_duration)

        if request.user.is_authenticated:
            # if user is authenticated the user id needs to be serialized
            print("user is authenticated", request.user)
            print(parking_spot_id)
        else:
            # if the user is not authenticated the user email needs to be provided instead
            email = request.data["reservation"]["email"]
            data = {
                "email": email,
                "parking_spot": parking_spot_id,
                "start_time": time_now,
                "end_time": time_now + time_delta,
            }

        # serialize the data stream
        serializer = ReservationSerializer(data=data)

        # throw a validation exception and send a response if validation fails
        serializer.is_valid(raise_exception=True)

        # otherwise save the new reservation
        serializer.save()

        # and set the related parking spot status to reserved=true
        parking_spot = ParkingSpot.objects.get(id=parking_spot_id)
        parking_spot.reserved = True
        parking_spot.save()

        # declare the response variable such that the email or user key can be removed before
        # sending a JSON response
        response = serializer.data

        if request.user.is_authenticated:
            del response["email"]
            return Response(data=response)
        else:
            del response["user"]
            return Response(data=response)
