"""
This module contains all the url patterns which direct requests to the relevant views.
"""

from django.urls import path

from .views.auth_views import ChangePw, SignInView, SignOutView, SignUpView
from .views.parking_spot_views import (
    GetAvailableParkingSpotsFilterView,
    GetAvailableParkingSpotsView,
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
    # available-parking-spots-radial?lat=0.123456&long=0.123456&unit=meter&distance=100
    path(
        "available-parking-spots-filter",
        GetAvailableParkingSpotsFilterView.as_view(),
        name="api-available-parking-spots-filter",
    ),
]
