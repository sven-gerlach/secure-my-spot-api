"""
Module for creating Stripe payment intent
"""

# Import Django / rest-framework modules
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

# Import Django models / serializers
from app.models.reservation import Reservation
from app.serializers.reservation_serializer import ReservationSerializer

# Import utility modules
from utils.payments import get_total_reservation_fee
import stripe
import os


# set secret test API key
stripe.api_key = os.getenv("STRIPE_API_TEST_KEY")


class PaymentView(APIView):
    """
    Set up a Stripe payment intent
    """

    def post(self, request):
        """
        Create payment intent and return the client_secret.
        Request object must contain the reservation_id as well as the matching email.
        """

        print(request)
        data = request.data
        print(data)
        reservation = get_object_or_404(Reservation, id=data["reservation_id"])

        # setup Stripe payment intent variable
        intent = None

        if reservation.email == data["email"]:
            # create a new Stripe payment intent
            intent = stripe.PaymentIntent.create(
                currency="usd",
                amount=int(get_total_reservation_fee(data["reservation_id"]) * 100),
                automatic_payment_methods={"enabled": True},
                receipt_email=data["email"],
            )
        else:
            # send a response signalling the authorisation issue
            return JsonResponse(
                {"authorisation": "The provided email and reservation_id do not match"},
                status=401
            )

        # add payment_intent_id to reservation resource
        data = {"stripe_payment_intent_id": intent.id}
        serializer = ReservationSerializer(reservation, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"clientSecret": intent["client_secret"]}, status=201)
