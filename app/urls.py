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
    CreateReservationView,
    GetActiveReservations,
    GetExpiredReservations,
    GetReservationView,
)

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
    # reservation routes
    # a sample path to this route is of the following format: reservation/18, meaning create a
    # reservation for the parking spot with id=18. The data of the request will either contain
    # the token (authenticated) or the user's email. Additionally the data will contain the
    # length of reservation period in minutes
    path(
        "reservation/<int:parking_spot_id>/",
        CreateReservationView.as_view(),
        name="api-create-reservation",
    ),
    # this reservation route returns a specific reservation, as identified by the reservationID
    # and a matching user's email, for unauthenticated users
    path(
        "reservation/<int:reservation_id>/<str:email>/",
        GetReservationView.as_view(),
        name="api-get-reservation",
    ),
    # route for retrieving all active reservations for an authenticated user
    path(
        "active-reservations/",
        GetActiveReservations.as_view(),
        name="api-get-active-reservations",
    ),
    # route for retrieving all expired reservations for an authenticated user
    path(
        "expired-reservations/",
        GetExpiredReservations.as_view(),
        name="api-get-expired-reservations",
    ),
]
