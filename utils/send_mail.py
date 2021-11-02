"""
Module which sends an email via the Sendinblue SMTP server
"""

from datetime import datetime
from django.core.mail import send_mail


def send_reservation_confirmation_mail(
        user_mail_address: str,
        parking_spot_id: str,
        reservation_id: str,
        start_time: datetime,
        end_time: datetime
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

    message = f"""
    Dear User,
    
    This email confirms your reservation of a parking spot in New York City. Please note the 
    reservation details below. We will send you another email 5min before your reservation 
    expires to remind you and to give you the option to extend your reservation.
    
    Parking Spot ID: {parking_spot_id}
    Reservation ID: {reservation_id}
    Start Time: {start_time}
    End Time: {end_time}
    
    Note: all times are in EST
    
    Kindest regards,
    
    Secure-MY-Spot
    """

    # todo: create secure-my-spot email address on ProtonMail
    # todo: format start and end-times
    # todo: change system time zone to EST
    send_mail(
        subject="Reservation Confirmation",
        message=message,
        from_email="svengerlach@me.com",
        recipient_list=[user_mail_address]
    )
