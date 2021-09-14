from django.urls import path
from .views.auth_views import SignUp

urlpatterns = [
    path("sign-up/", SignUp.as_view(), name="sign-up"),
]
