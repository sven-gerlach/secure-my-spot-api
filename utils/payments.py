"""
Module for payments processing
"""

import os
from app.models.reservation import Reservation
import stripe


def get_total_reservation_fee(reservation_id):
    """
    Return the total reservation fee based on the reservation duration and the hourly rate,
    formatted to two decimal places
    """

    reservation = Reservation.objects.get(id=reservation_id)
    duration_minutes = reservation.duration
    rate_per_hour = reservation.rate
    return round(duration_minutes * rate_per_hour / 60, 2)


def get_customer_id(email):
    """
    Returns the Stripe customer_id.
    If the user with email already exists as a Stripe customer, this function returns the
    relevant customer_id. If no such user exists, the function creates a new Stripe customer and
    returns the associated customer_id.
    """

    # set secret test API key
    stripe.api_key = os.getenv("STRIPE_API_TEST_KEY")

    # retrieve all Stripe customers with email=email
    customers = stripe.Customer.list(email=email)

    # if no customer with this email address exists, create a new customer and return
    if len(customers["data"]) == 0:
        new_customer_object = stripe.Customer.create(email=email)
        return new_customer_object.id

    if len(customers["data"]) == 1:
        return customers["data"][0]["id"]

    # raise and exception if two or more customers have the same email address
    raise Exception("Two or more Stripe customers have the same email address")


def charge_customer(reservation_id):
    """
    Retrieve stripe_setup_intent_id from database. Use that id to retrieve the setup intent
    object which includes the customer id. Retrieve the payment method id with the customer_id.
    Create a payment intent with the customer_id and payment_method_id.
    """

    # retrieve stripe_setup_intent_id from reservation resource
    reservation = Reservation.objects.get(id=reservation_id)
    stripe_setup_intent_id = reservation.stripe_setup_intent_id

    # set secret test API key
    stripe.api_key = os.getenv("STRIPE_API_TEST_KEY")

    # retrieve setup_intent object
    setup_intent = stripe.SetupIntent.retrieve(id=stripe_setup_intent_id)

    # assign customer_id and payment_method_id
    stripe_customer_id = setup_intent.customer
    stripe_payment_method_id = setup_intent.payment_method

    payment_amount = int(get_total_reservation_fee(reservation_id) * 100)

    if payment_amount >= 1:
        try:
            #  create payment intent
            stripe.PaymentIntent.create(
                amount=payment_amount,
                currency="usd",
                customer=stripe_customer_id,
                payment_method=stripe_payment_method_id,
                off_session=True,
                confirm=True,
            )

            # set paid field to True
            reservation = Reservation.objects.get(id=reservation_id)
            reservation.paid = True
            reservation.save()
        except stripe.error.CardError as e:
            err = e.error

            # Error code will be authentication_required if authentication is needed
            msg_string = "Attempt to collect from customer {customer} threw error code {code}"
            print(msg_string.format(customer=stripe_customer_id, code=err.code))
    else:

        # set paid field to True
        reservation = Reservation.objects.get(id=reservation_id)
        reservation.paid = True
        reservation.save()


def get_stripe_payment_method_object(reservation_id):
    """
    Return the stripe payment method object
    """

    reservation = Reservation.objects.get(id=reservation_id)

    stripe_setup_intent_id = reservation.stripe_setup_intent_id

    # retrieve setup intent
    intent = stripe.SetupIntent.retrieve(id=stripe_setup_intent_id)
    payment_method_id = intent.payment_method

    # retrieve payment method object
    return stripe.PaymentMethod.retrieve(id=payment_method_id)
