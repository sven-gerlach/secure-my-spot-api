"""
This module contains all the url patterns which direct requests to the relevant views.
"""

from django.urls import path

from .views.auth_views import ChangePw, SignInView, SignOutView, SignUpView

urlpatterns = [
    path("sign-up/", SignUpView.as_view()),
    path("sign-in/", SignInView.as_view()),
    path("sign-out/", SignOutView.as_view()),
    path("change-pw/", ChangePw.as_view()),
]
