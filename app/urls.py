from django.urls import path

from .views.auth_views import SignUpView

urlpatterns = [
    path("sign-up/", SignUpView.as_view()),
]
