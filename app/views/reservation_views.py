"""
Module for all reservation views
"""

# import Python modules
import datetime

# import Django / RestFramework modules
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# import utils
from utils.payments import get_stripe_payment_method_object
from utils.send_mail import send_reservation_amendment_confirmation_mail

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

        # setup the components that make up the data object that needs serializing
        rate = ParkingSpot.objects.get(id=parking_spot_id).rate
        # create datetime object and strip seconds and microseconds off
        time_now = datetime.datetime.now().replace(second=0, microsecond=0)
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
        task = unreserve_parking_spot.apply_async(
            args=[parking_spot_id, serializer.data["id"]],
            countdown=float(reservation_duration * 60),
        )

        print("============= task object START =============")
        print(dir(task))
        print("============= task object END =============")

        # save key / value pair of reservation_id / task_id
        cache.set(serializer.data["id"], task.task_id)

        # declare the response variable such that the email or user key can be removed before
        # sending a JSON response
        response = serializer.data

        # send the response
        return Response(data=response)

    def get(self, request):
        """
        Retrieve all active reservations owned by authenticated user and return the serialized
        result
        """

        active_reservations = Reservation.objects.filter(paid=False, user=request.user)
        sorted_active_reservations = active_reservations.order_by("-start_time")
        serializer = ReservationSerializer(sorted_active_reservations, many=True)
        return Response(serializer.data)

    def patch(self, request, reservation_id):
        """
        This view updates the end_time of a reservation with the data provided by the authenticated
        client
        """

        # retrieve relevant reservation from db
        reservation = get_object_or_404(
            Reservation, id=reservation_id, user=request.user
        )

        # convert date_time str into Python datetime object
        end_time_str = request.data["reservation"]["end_time"]
        conversion_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        end_time = datetime.datetime.strptime(end_time_str, conversion_format)

        # replace seconds and microseconds
        end_time = end_time.replace(second=0, microsecond=0)

        # set end_time on data dictionary
        data = {"end_time": end_time}

        serializer = ReservationSerializer(reservation, data=data, partial=True)

        serializer.is_valid(raise_exception=True)

        serializer.save()

        # retrieve task_id associated with reservation_id from Redis cache
        cache.get(serializer.data["id"])

        # revoke existing task to reset availability of reserved parking spot
        # this feature did not work because the worker got shut down automatically by Heroku
        # https://stackoverflow.com/questions/8920643/cancel-an-already-executing-task-with-celery
        # app.control.revoke(task_id=task_id, terminate=True)

        # set new task with new end_time param
        task = unreserve_parking_spot.apply_async(
            args=[reservation.parking_spot.id, reservation.id],
            eta=reservation.end_time,
        )

        print("============= task object START =============")
        print(dir(task))
        print("============= task object END =============")

        # save reservation_id / task_id key / value pair in Redis cache
        cache.set(serializer.data["id"], task.task_id)

        # send email to user, confirming amended reservation details
        # if end_time is within the next two minutes, do not send an amendment confirmation email,
        # instead just rely on expiration email
        if end_time - datetime.datetime.now() > datetime.timedelta(minutes=1):
            payment_method = get_stripe_payment_method_object(reservation_id)

            # send email to user, confirming amended reservation details
            send_reservation_amendment_confirmation_mail(
                user_mail_address=reservation.email,
                parking_spot_id=reservation.parking_spot.id,
                rate=reservation.rate,
                reservation_id=reservation.id,
                start_time=reservation.start_time,
                end_time=reservation.end_time,
                last4card=payment_method.card["last4"],
            )

        return Response(data=serializer.data, status=200)

    def delete(self, request, reservation_id):
        """
        This end-point is called if a reservation was made but the payment process was not
        completed on the front-end side, usually because the user navigated away from the
        Stripe payments page or the payments process failed in another way.
        """

        reservation = get_object_or_404(
            Reservation, id=reservation_id, email=request.user.email
        )
        # reset parking spot availability
        reservation.parking_spot.reserved = False

        # delete reservation
        reservation.delete()

        return Response(status=204)


class ReservationViewUnauth(APIView):
    """
    API view for creating a new reservation, retrieving a specific reservation and changing a
    specific reservation.
    """

    def post(self, request, parking_spot_id):
        """
        Create a new reservation resource associated with an unauthenticated user's email and a
        parking spot. Once the reservation resource is created, create a Stripe payment intent.
        Add the payment intent id to the reservation resource. Set the parking spot status to
        reserved. Return the reservation resource to the client.
        """

        # setup the components that make up the data object that needs serializing
        rate = ParkingSpot.objects.get(id=parking_spot_id).rate
        # create datetime object and strip seconds and microseconds off
        time_now = datetime.datetime.now().replace(second=0, microsecond=0)
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

        # set the related parking spot status to reserved=true
        parking_spot = get_object_or_404(ParkingSpot, id=parking_spot_id)
        parking_spot.reserved = True
        parking_spot.save()

        # set a task that makes the same parking spot available for reservation again after the
        # reservation length is up
        task = unreserve_parking_spot.apply_async(
            args=[parking_spot_id, serializer.data["id"]],
            eta=time_now + time_delta,
        )

        print("============= task object START =============")
        print(dir(task))
        print("============= task object END =============")

        # save key / value pair of reservation_id / task_id to Redis cache
        cache.set(serializer.data["id"], task.task_id)

        # declare the response variable
        response = serializer.data

        # send the response to the client
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
                    "error": "This reservation belongs to an authenticated account. "
                    "Please login to review this reservation."
                },
                status=401,
            )

        # serialize the data
        serializer = ReservationSerializer(reservation)

        # send the response
        return Response(serializer.data, status=200)

    def patch(self, request, reservation_id, email):
        """
        This view updates the end_time of a reservation with the data provided by the
        unauthenticated client
        """

        # retrieve reservation from db
        reservation = get_object_or_404(Reservation, id=reservation_id, email=email)

        # convert date_time str into Python datetime object
        end_time_str = request.data["reservation"]["end_time"]
        conversion_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        end_time = datetime.datetime.strptime(end_time_str, conversion_format)

        # replace seconds and microseconds with zero
        end_time = end_time.replace(second=0, microsecond=0)

        # set end_time on data dictionary
        data = {"end_time": end_time}

        serializer = ReservationSerializer(reservation, data=data, partial=True)

        serializer.is_valid(raise_exception=True)

        # save the new reservation instance
        serializer.save()

        # retrieve task_id associated with reservation_id from Redis cache
        cache.get(serializer.data["id"])

        # set new task with new end_time param
        task = unreserve_parking_spot.apply_async(
            args=[reservation.parking_spot.id, reservation.id],
            eta=reservation.end_time,
        )

        print("============= task object START =============")
        print(dir(task))
        print("============= task object END =============")

        # save reservation_id / task_id key / value pair in Redis cache
        cache.set(serializer.data["id"], task.task_id)

        # send email to user, confirming amended reservation details
        # if end_time is within the next two minutes, do not send an amendment confirmation email,
        # instead just rely on expiration email
        if end_time - datetime.datetime.now() > datetime.timedelta(minutes=1):
            payment_method = get_stripe_payment_method_object(reservation.id)
            send_reservation_amendment_confirmation_mail(
                user_mail_address=reservation.email,
                parking_spot_id=reservation.parking_spot.id,
                rate=reservation.rate,
                reservation_id=reservation.id,
                start_time=reservation.start_time,
                end_time=reservation.end_time,
                last4card=payment_method.card["last4"],
            )

        # return response to client
        return Response(data=serializer.data, status=200)

    def delete(self, request, reservation_id, email):
        """
        This end-point is called if a reservation was made but the payment process was not
        completed on the front-end side, usually because the user navigated away from the
        Stripe payments page or the payments process failed in another way.
        """

        reservation = get_object_or_404(Reservation, id=reservation_id, email=email)

        # reset parking spot availability
        parking_spot = ParkingSpot.objects.get(id=reservation.parking_spot.id)
        parking_spot.reserved = False
        parking_spot.save()

        # delete reservation
        reservation.delete()

        return Response(status=204)


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
        sorted_expired_reservations = expired_reservations.order_by("-start_time")
        serializer = ReservationSerializer(sorted_expired_reservations, many=True)
        return Response(serializer.data)
