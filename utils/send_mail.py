"""
Module which sends an email via the Sendinblue SMTP server
"""

from datetime import datetime
import pytz
from django.core.mail import send_mail
from decimal import Decimal
from app.models.reservation import Reservation
from utils.payments import get_total_reservation_fee, get_stripe_payment_method_object


def send_reservation_confirmation_mail(
        user_mail_address: str,
        parking_spot_id: int,
        rate: Decimal,
        reservation_id: float,
        start_time: datetime,
        end_time: datetime,
        last4card: str,
):
    """
    Send an email to the user, confirming their reservation.

    Params
    ------
    user_mail_address: email address of the user
    parking_spot_id: id of the reserved parking spot
    reservation_id: id of the reservation
    start_time: reservation start time
    end_time: reservation end time
    """

    reservation_fee = get_total_reservation_fee(reservation_id)

    # time zone formatting
    est_tz = pytz.timezone("US/Eastern")
    start_time_est = start_time.astimezone(est_tz)
    end_time_est = end_time.astimezone(est_tz)
    fmt = "%H:%M"

    message = f"""
    Dear User,
    
    This email confirms your reservation of a parking spot in New York City. Please note the 
    reservation details below.
    
    Parking Spot ID: {parking_spot_id}
    Reservation ID: {reservation_id}
    Rate / hour (USD): {rate}
    Start Time: {start_time_est.strftime(fmt)}
    End Time: {end_time_est.strftime(fmt)}
    Reservation Fee (USD): {reservation_fee}
    Payment Details: xxxx-xxxx-xxxx-{last4card}
    Payment Processed: not yet
    
    Note: all times are New York Time (EST)
    
    Kindest regards,
    
    Secure My Spot
    """

    send_mail(
        subject="Reservation Confirmation",
        message=message,
        from_email="Secure My Spot <donotreply@secure-my-spot.com>",
        recipient_list=[user_mail_address]
    )


def send_reservation_amendment_confirmation_mail(
        user_mail_address: str,
        parking_spot_id: str or int,
        rate: Decimal,
        reservation_id: int,
        start_time: datetime,
        end_time: datetime,
        last4card: str,
):
    """
    Send email to user confirming the amended reservation details
    """

    reservation_fee = get_total_reservation_fee(reservation_id)

    # time zone formatting
    est_tz = pytz.timezone("US/Eastern")
    start_time_est = start_time.astimezone(est_tz)
    end_time_est = end_time.astimezone(est_tz)
    fmt = "%H:%M"

    message = f"""
        Dear User,

        This email confirms your amended reservation of a parking spot in 
        New York City. Please note the reservation details below.

        Parking Spot ID: {parking_spot_id}
        Reservation ID: {reservation_id}
        Rate / hour (USD): {rate}
        Start Time: {start_time_est.strftime(fmt)}
        End Time: {end_time_est.strftime(fmt)}
        Reservation Fee (USD): {reservation_fee}
        Payment Details: xxxx-xxxx-xxxx-{last4card}
        Payment Processed: not yet

        Note: all times are New York Time (EST)

        Kindest regards,

        Secure My Spot
        """

    send_mail(
        subject="Reservation Amendment",
        message=message,
        from_email="Secure My Spot <donotreply@secure-my-spot.com>",
        recipient_list=[user_mail_address]
    )


def send_reservation_has_ended_mail(reservation_id):
    """
    Send email to user confirming that their reservation of the reserved parking spot has ended
    and that their provided payment method will now be used to process the final amount.
    """

    reservation = Reservation.objects.get(id=reservation_id)
    reservation_fee = get_total_reservation_fee(reservation_id)

    # retrieve payment method associated with this reservation
    payment_method = get_stripe_payment_method_object(reservation_id)

    message = f"""
    Dear User,
    
    Your reservation of parking spot {reservation.parking_spot.id} has now ended. The total 
    reservation fee of USD {reservation_fee} will be charged to the card ending in {payment_method.card["last4"]}
    immediately.
    
    Thank you for your business. We look forward to helping you find parking in New York City soon.
    
    Kindest regards,
    
    Secure My Spot
    """

    send_mail(
        subject="Reservation Has Ended",
        message=message,
        from_email="Secure My Spot <donotreply@secure-my-spot.com>",
        recipient_list=[reservation.email]
    )
