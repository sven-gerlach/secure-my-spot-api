"""
Module for processing all Stripe related payments processing tasks
"""

import stripe
import os
from utils.payments import get_total_reservation_fee


def create_payment_intent(reservation_id, user_id):
    """
    Create payment intent and return the payment_intent_id and client_secret
    """

    # set secret test API key
    stripe.api_key = os.getenv("STRIPE_API_TEST_KEY")

    intent = stripe.PaymentIntent.create(
        currency="usd",
        amount=int(get_total_reservation_fee(reservation_id) * 100),
        automatic_payment_methods={"enabled": True},
        receipt_email=user_id
    )

    print(intent)

    return intent["id"], intent["client_secret"]
