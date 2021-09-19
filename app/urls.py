from django.urls import path

from .views.auth_views import signup_view

urlpatterns = [
    path("sign-up/", signup_view),
]
