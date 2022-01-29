"""
Module for creating Stripe payment intent
"""

# Python modules
import os

import stripe
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

# Import Django / rest-framework modules
from rest_framework.views import APIView

# Import Django models / serializers
from app.models.reservation import Reservation
from app.serializers.reservation_serializer import ReservationSerializer
from utils.payments import get_customer_id, get_stripe_payment_method_object

# Import utility modules
from utils.send_mail import send_reservation_confirmation_mail

# set secret test API key

stripe.api_key = os.getenv("STRIPE_API_TEST_KEY")


class PaymentViewUnauth(APIView):
    """
    Set up a Stripe payment intent
    """

    def post(self, request):
        """
        Create SetupIntent and return the client_secret.
        Request object must contain the reservation_id as well as the matching email.
        """

        data = request.data
        reservation = get_object_or_404(Reservation, id=data["reservation_id"])

        # setup Stripe payment intent variable
        intent = None

        # verify that provided email address is indeed the one registered on the reservation
        # resource
        if reservation.email == data["email"]:
            # retrieve or create customer_od
            customer_id = get_customer_id(email=reservation.email)

            # create a new Stripe SetupIntent
            intent = stripe.SetupIntent.create(
                customer=customer_id,
                payment_method_types=["card"],
            )
        else:
            # send a response signalling the authorisation issue
            return JsonResponse(
                {"authorisation": "The provided email and reservation_id do not match"},
                status=401,
            )

        # add setup_intent_id to reservation resource
        data = {"stripe_setup_intent_id": intent.id}
        serializer = ReservationSerializer(reservation, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"clientSecret": intent.client_secret}, status=201)

    def get(self, request, reservation_id, email):
        """
        This method is only called by the client if the setup intent was successful. This method
        sends the reservation confirmation email to the user.
        """

        reservation = get_object_or_404(Reservation, id=reservation_id, email=email)

        payment_method = get_stripe_payment_method_object(reservation_id)

        # send reservation confirmation email to user
        # pass datetime format instead of stringified time from response object
        send_reservation_confirmation_mail(
            user_mail_address=reservation.email,
            parking_spot_id=reservation.parking_spot.id,
            rate=reservation.rate,
            reservation_id=reservation.id,
            start_time=reservation.start_time,
            end_time=reservation.end_time,
            last4card=payment_method.card["last4"],
        )

        return Response(status=204)
