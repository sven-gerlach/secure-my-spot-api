"""
This module contains all the url patterns which direct requests to the relevant views.
"""

from django.urls import path

from .views.auth_views import ChangePw, SignInView, SignOutView, SignUpView
from .views.parking_spot_views import GetAllParkingSpotsView

urlpatterns = [
    # auth routes
    path("sign-up/", SignUpView.as_view(), name="api-sign-up"),
    path("sign-in/", SignInView.as_view(), name="api-sign-in"),
    path("sign-out/", SignOutView.as_view(), name="api-sign-out"),
    path("change-pw/", ChangePw.as_view(), name="api-change-pw"),
    # parking spot routes
    path(
        "available-parking-spots/",
        GetAllParkingSpotsView.as_view(),
        name="api-available-parking-spots",
    ),
]
