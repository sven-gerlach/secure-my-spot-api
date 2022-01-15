"""
This module contains all the url patterns which direct requests to the relevant views.
"""

from django.urls import path

from .views.auth_views import ChangePw, SignInView, SignOutView, SignUpView
from .views.parking_spot_views import (
    GetAvailableParkingSpotsFilterView,
    GetAvailableParkingSpotsView,
)
from .views.reservation_views import (
    GetExpiredReservationsAuth,
    ReservationViewAuth,
    ReservationViewUnauth,
)
from .views.payment_views import PaymentView

urlpatterns = [
    # auth routes
    path("sign-up/", SignUpView.as_view(), name="api-sign-up"),
    path("sign-in/", SignInView.as_view(), name="api-sign-in"),
    path("sign-out/", SignOutView.as_view(), name="api-sign-out"),
    path("change-pw/", ChangePw.as_view(), name="api-change-pw"),
    # parking spot routes
    path(
        "available-parking-spots/",
        GetAvailableParkingSpotsView.as_view(),
        name="api-available-parking-spots",
    ),
    # the client is expected to send the filter keys (location, unit, distance) in query strings
    # a request for all available parking spots around the GPS point (0.123456,0.123456) within a
    # 100 meter radius would look like this:
    # available-parking-spots-radial?lat=0.123456&lng=0.123456&unit=km&dist=0.1
    path(
        "available-parking-spots-filter",
        GetAvailableParkingSpotsFilterView.as_view(),
        name="api-available-parking-spots-filter",
    ),
    # create reservation for authenticated user
    path(
        "reservation-auth/<int:parking_spot_id>/",
        ReservationViewAuth.as_view(),
        name="api-create-reservation-auth",
    ),
    # create reservation for unauthenticated user
    path(
        "reservation-unauth/<int:parking_spot_id>/",
        ReservationViewUnauth.as_view(),
        name="api-create-reservation-unauth",
    ),
    # route for retrieving all active reservations for an authenticated user
    path(
        "reservation-auth/",
        ReservationViewAuth.as_view(),
        name="api-retrieve-active-reservations-auth",
    ),
    # retrieve reservation for unauthenticated user with email and reservationID
    path(
        "reservation-unauth/<int:reservation_id>/<str:email>/",
        ReservationViewUnauth.as_view(),
        name="api-get-reservation-unauth",
    ),
    # route for retrieving all expired reservations for an authenticated user
    path(
        "expired-reservations-auth/",
        GetExpiredReservationsAuth.as_view(),
        name="api-get-expired-reservations-auth",
    ),
    # change a reservation for an authenticated user
    path(
        "update-reservation-auth/<int:reservation_id>/",
        ReservationViewAuth.as_view(),
        name="api-update-reservation-auth",
    ),
    # change a reservation for an unauthenticated user
    path(
        "update-reservation-unauth/<int:reservation_id>/<str:email>/",
        ReservationViewUnauth.as_view(),
        name="api-update-reservation-unauth",
    ),
    # setup a new Stripe payment intent
    path(
        "create-payment-intent/",
        PaymentView.as_view(),
        name="api-create-payment-intent",
    )
]
