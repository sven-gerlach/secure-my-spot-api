"""
Module for all views related to user authorisation
"""

import logging
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..serializers import AuthTokenSerializer, UserSerializer

logger = logging.getLogger(__name__)


class SignUpView(APIView):
    """Sign-up view"""
    def post(self, request):
        """
        Create and save a new user in the database
        """
        # parsing of incoming JSON data, including the sign-up credentials email and two
        # passwords, is not necessary since the JSON parser has been added to the REST framework
        # in settings.py. This will parse all incoming data and add it as a dictionary to
        # request.data
        # https://www.django-rest-framework.org/api-guide/parsers/#jsonparser
        data = request.data["credentials"]

        # if password_confirmation does not match the provided password, return 400 http error
        # with a meaningful error message
        if data.get("password") != data.get("password_confirmation"):
            return JsonResponse({"password": ["Passwords don't match."]}, status=400)

        # serialize data provided and create a new user object
        serializer = UserSerializer(data=data)

        # verify that new user object is valid and save the new user to the database if it is or
        # return http status 400 with error message otherwise
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


class SignInView(ObtainAuthToken):
    """
    Retrieve email and password from post request, confirm user with email exists and that the
    provided password matches with the stored and hashed password in the database. Create,
    store and return a token to the user. The user can use that token to authenticate themselves.
    """

    def post(self, request):
        """Create a return a token for authenticated users."""
        data = request.data["credentials"]
        serializer = AuthTokenSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        if not created:
            # If the token was not newly created then delete existing token and replace with a
            # new one. This forces the creation of a new token everytime the user logs in.
            # todo: add a time component such that tokens are automatically renewed after e.g. 24h
            token.delete()
            token = Token.objects.create(user=user)
            token.save()
            # whilst no changes have been made to any user fields, the user object must be saved
            # with the param update+fields set to the "last_login" field or else the field
            # wouldn't update
            # source: https://code.djangoproject.com/ticket/22981
            user.save(update_fields=["last_login"])
        return JsonResponse(
            {"token": token.key, "user_id": user.pk, "email": user.email}, status=201
        )


# todo: write tests for sign-out view
class SignOutView(APIView):
    """Sign out user provided user is authenticated and authorised to do so."""

    permission_classes = [IsAuthenticated]

    def delete(self, request):
        """Delete the user's token."""
        token = request.auth
        token.delete()
        return Response(status=200)
