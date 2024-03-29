"""
Module for all User model related tests
"""

import json
import logging

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate

from app.tests.factories import UserFactory, get_json_credentials
from app.views.auth_views import SignInView, SignOutView, SignUpView

# marking this module such that tests have access to the database
pytestmark = pytest.mark.django_db

# instantiates the django logger
logger = logging.getLogger(__name__)


class TestSignUpView:
    def test_signupview(self):
        """Http response code should be 201 and data={"email": "[...]", "password": "[...]"}"""
        # request factory generates a request instance that can be used as the first argument in a
        # view
        User = get_user_model()
        factory = APIRequestFactory()

        # https://www.django-rest-framework.org/api-guide/testing/
        # #explicitly-encoding-the-request-body
        credentials = get_json_credentials()
        request = factory.post(
            reverse("api-sign-up"),
            json.dumps(credentials),
            content_type="application/json",
        )

        # call the view with the request item
        response = SignUpView.as_view()(request)

        # test assertions
        assert response.status_code == 201
        assert User.objects.count() == 1
        assert User.objects.last().email == credentials["credentials"]["email"]

    def test_signupview_api(self):
        user = UserFactory.build()
        client = APIClient()
        response = client.post(
            reverse("api-sign-up"),
            {
                "credentials": {
                    "email": user.email,
                    "password": user.password,
                    "password_confirmation": user.password,
                }
            },
            format="json",
        )
        # assert user is crated and stored in the db
        assert get_user_model().objects.get(email=user.email).email == user.email
        assert response.status_code == 201

    def test_signupview_missing_email(self):
        """Missing email http response code of 400 and data for email=["This field is required."]"""
        # request factory generates a request instance that can be used as the first argument in a
        # view
        factory = APIRequestFactory()

        # https://www.django-rest-framework.org/api-guide/testing/
        # #explicitly-encoding-the-request-body
        credentials = get_json_credentials()
        # remove email from credentials
        credentials["credentials"].pop("email", None)
        request = factory.post(
            reverse("api-sign-up"),
            json.dumps(credentials),
            content_type="application/json",
        )

        # call the view with the request item
        response = SignUpView.as_view()(request)

        # render response
        response.render()

        # test assertions
        assert response.status_code == 400
        assert json.loads(response.content) == {"email": ["This field is required."]}

    def test_signupview_blank_email(self):
        """Missing email http response code of 400 and data for email=["This field is required."]"""
        """Missing email http response code of 400 and data for email=["This field is required."]"""
        # request factory generates a request instance that can be used as the first argument in a
        # view
        factory = APIRequestFactory()

        # https://www.django-rest-framework.org/api-guide/testing/
        # #explicitly-encoding-the-request-body
        credentials = get_json_credentials(email="")
        request = factory.post(
            reverse("api-sign-up"),
            json.dumps(credentials),
            content_type="application/json",
        )

        # call the view with the request item
        response = SignUpView.as_view()(request)

        # render response
        response.render()

        # test assertions
        assert response.status_code == 400
        assert json.loads(response.content) == {
            "email": ["This field may not be blank."]
        }

    def test_signupview_missing_password(self):
        """
        Missing email http response code of 400 and data for password=["This field is required."]
        """
        # request factory generates a request instance that can be used as the first argument in a
        # view
        factory = APIRequestFactory()

        # https://www.django-rest-framework.org/api-guide/testing/
        # #explicitly-encoding-the-request-body
        credentials = get_json_credentials()
        # remove password from credentials
        credentials["credentials"].pop("password", None)
        credentials["credentials"].pop("password_confirmation", None)
        request = factory.post(
            reverse("api-sign-up"),
            json.dumps(credentials),
            content_type="application/json",
        )

        # call the view with the request item
        response = SignUpView.as_view()(request)

        # render response
        response.render()

        # test assertions
        assert response.status_code == 400
        assert json.loads(response.content) == {"password": ["This field is required."]}

    def test_signupview_non_matching_passwords(self):
        """Missing email http response code of 400 and data [...]"""
        # request factory generates a request instance that can be used as the first argument in a
        # view
        factory = APIRequestFactory()

        # https://www.django-rest-framework.org/api-guide/testing/
        # #explicitly-encoding-the-request-body
        credentials = get_json_credentials(
            password_confirmation="wrong password confirmation"
        )
        request = factory.post(
            reverse("api-sign-up"),
            json.dumps(credentials),
            content_type="application/json",
        )

        # call the view with the request item
        response = SignUpView.as_view()(request)

        # test assertions
        assert response.status_code == 400
        assert json.loads(response.content) == {
            "password_error": ["Passwords do not match"]
        }

    def test_signupview_user_already_exists(self):
        """Missing email http response code of 400 and data for email=["user with this email
        address already exists."]"""
        # request factory generates a request instance that can be used as the first argument in a
        # view
        factory = APIRequestFactory()

        # https://www.django-rest-framework.org/api-guide/testing/
        # #explicitly-encoding-the-request-body
        credentials = get_json_credentials()
        request = factory.post(
            reverse("api-sign-up"),
            json.dumps(credentials),
            content_type="application/json",
        )

        # create a user in the database with the same credentials
        User = get_user_model()
        User.objects.create_user(
            email=credentials["credentials"]["email"],
            password=credentials["credentials"]["password"],
        )

        # call the sign-up view with the request item
        response = SignUpView.as_view()(request)

        # render the response first
        response.render()

        # test assertions
        assert response.status_code == 400
        assert json.loads(response.content) == {
            "email": ["user with this email address already exists."]
        }


class TestSignInView:
    def test_signinview(self):
        """Validate that token is stored in database on user object, http code is 201, and that the
        same token is successfully returned to the client {"token": "[...]"}"""
        # create credentials
        credentials = get_json_credentials()

        # create a user with credentials
        User = get_user_model()
        user = User.objects.create_user(
            email=credentials["credentials"]["email"],
            password=credentials["credentials"]["password"],
        )

        # create a request object
        factory = APIRequestFactory()
        request = factory.post(
            reverse("api-sign-in"),
            json.dumps(credentials),
            content_type="application/json",
        )

        # retrieve the response object by calling the view function with the request objects
        response = SignInView.as_view()(request)

        # test assertions
        assert response.status_code == 200
        assert json.loads(response.content) == {
            "email": user.email,
            "token": Token.objects.get(user=user).key,
        }

    def test_signinview_email_does_not_exist(self):
        """Return error message to user with http code 404 and message {"email": ["This user does
        not exist."]}"""
        # create a request object
        factory = APIRequestFactory()
        credentials = get_json_credentials()
        request = factory.post(
            reverse("api-sign-in"),
            json.dumps(credentials),
            content_type="application/json",
        )

        # retrieve the response object by calling the view function with the request objects
        response = SignInView.as_view()(request)

        # Template based responses need to be manually rendered before their response.content can be
        # inspected
        response.render()

        # test assertions
        assert response.status_code == 400
        assert json.loads(response.content) == {
            "non_field_errors": ["Unable to log in with provided credentials."]
        }

    def test_signinview_incorrect_password(self):
        """Return error message to user with http code 401 and message {"password": ["Incorrect
        password!"]}"""
        # credentials
        credentials = get_json_credentials()

        # create user with these credentials
        User = get_user_model()
        User.objects.create_user(
            email=credentials["credentials"]["email"],
            password=credentials["credentials"]["password"],
        )

        # create a request object for sign-in view
        factory = APIRequestFactory()
        request = factory.post(
            reverse("api-sign-in"),
            json.dumps(credentials),
            content_type="application/json",
        )

        # retrieve the response object by calling the view function with the request objects
        response = SignInView.as_view()(request)

        # create a request object
        factory = APIRequestFactory()
        credentials["credentials"]["password"] = "wrong password"
        request = factory.post(
            reverse("api-sign-in"),
            json.dumps(credentials),
            content_type="application/json",
        )

        # retrieve the response object by calling the view function with the request objects
        response = SignInView.as_view()(request)

        # Template based responses need to be manually rendered before their response.content can be
        # inspected
        response.render()

        # test assertions
        assert response.status_code == 400
        assert json.loads(response.content) == {
            "non_field_errors": ["Unable to log in with provided credentials."]
        }


class TestSignOutView:
    """test sign out view"""

    def test_signoutview(self):
        """Successful sign-out results in client receiving a response status code of 200 and the
        deletion of the client's token from the db."""
        # create faker credentials
        credentials = get_json_credentials()

        # create a user with fake credentials
        User = get_user_model()
        user = User.objects.create_user(
            email=credentials["credentials"]["email"],
            password=credentials["credentials"]["password"],
        )

        # create a request object for sign-in view
        factory = APIRequestFactory()
        request = factory.post(
            reverse("api-sign-in"),
            json.dumps(credentials),
            content_type="application/json",
        )

        # sign the user in with the request object and retrieve the token associated with the
        # signed-in user
        SignInView.as_view()(request)
        token_obj = Token.objects.get(user=user)

        # create request object for sign-out view
        request = factory.delete(reverse("api-sign-out"))
        force_authenticate(request, user=user, token=token_obj)
        response = SignOutView.as_view()(request)

        # test assertions
        assert response.status_code == 204
        with pytest.raises(ObjectDoesNotExist):
            Token.objects.get(user=user)

    def test_signoutview_invalid_token(self):
        """An unauthorised attempt to sign out with an invalid token results in the client
        receiving a 401 status code and a json response {"detail": "Invalid token."}."""
        # create request object for sign-out view without submitting a token
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Token " + "InvalidToken")
        response = client.delete(reverse("api-sign-out"))

        # test assertions
        assert response.status_code == 401
        assert json.loads(response.content) == {"detail": "Invalid token."}

    def test_signoutview_missing_token(self):
        """An unauthenticated attempt to sign out with a missing token results in the client
        receiving a 401 status code."""
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="TOKEN ")
        response = client.delete(reverse("api-sign-out"))

        # test assertions
        assert response.status_code == 401
        assert json.loads(response.content) == {
            "detail": "Invalid token header. No credentials " "provided."
        }


class TestChangePw:
    """test ChangePw view"""

    def test_changepwview(self):
        # create faker credentials
        credentials = get_json_credentials()

        # create a user with fake credentials
        User = get_user_model()
        user = User.objects.create_user(
            email=credentials["credentials"]["email"],
            password=credentials["credentials"]["password"],
        )

        # create a request object for sign-in view
        factory = APIRequestFactory()
        request = factory.post(
            reverse("api-sign-in"),
            json.dumps(credentials),
            content_type="application/json",
        )

        # sign the user in with the request object and retrieve the token associated with the
        # signed-in user
        SignInView.as_view()(request)
        token_obj = Token.objects.get(user=user)

        # use APIClient and the token to request a password change
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="TOKEN " + f"{token_obj.key}")
        response = client.patch(
            reverse("api-change-pw"),
            {
                "credentials": {
                    "email": credentials["credentials"]["email"],
                    "password": credentials["credentials"]["password"],
                    "new_password": "a new password",
                    "new_password_confirmed": "a new password",
                }
            },
            format="json",
        )

        # test assertions
        assert response.status_code == 204

    def test_changepwview_unauthenticated(self):
        """Expect status code of 401 and response content of {"detail": {"Invalid token header.
        No credentials provided."}}"""
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="TOKEN ")
        response = client.patch(
            reverse("api-change-pw"),
            {
                "credentials": {
                    "password": "a new password",
                    "password_confirmation": "a new password",
                }
            },
            format="json",
        )

        # test assertions
        assert response.status_code == 401
        assert json.loads(response.content) == {
            "detail": "Invalid token header. No credentials provided."
        }

    def test_changepwview_passwords_dont_match(self):
        """Expect status code of 400 and response content of {"detail": "Passwords don't match"}"""
        # create faker credentials
        credentials = get_json_credentials()

        # create a user with fake credentials
        User = get_user_model()
        user = User.objects.create_user(
            email=credentials["credentials"]["email"],
            password=credentials["credentials"]["password"],
        )

        # create a request object for sign-in view
        factory = APIRequestFactory()
        request = factory.post(
            reverse("api-sign-in"),
            json.dumps(credentials),
            content_type="application/json",
        )

        # sign the user in with the request object and retrieve the token associated with the
        # signed-in user
        SignInView.as_view()(request)
        token_obj = Token.objects.get(user=user)

        # use APIClient and the token to request a password change
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="TOKEN " + f"{token_obj.key}")
        response = client.patch(
            reverse("api-change-pw"),
            {
                "credentials": {
                    "email": credentials["credentials"]["email"],
                    "password": credentials["credentials"]["password"],
                    "new_password": "a new password",
                    "new_password_confirmed": "a new different password",
                }
            },
            format="json",
        )

        # test assertions
        assert response.status_code == 400
        assert json.loads(response.content) == {
            "password_error": "Passwords do not match"
        }

    def test_changepwview_missing_new_passwords(self):
        """
        Expect status code of 400 and response content of {"detail": "No new passwords provided"}
        """
        # create faker credentials
        credentials = get_json_credentials()

        # create a user with fake credentials
        User = get_user_model()
        user = User.objects.create_user(
            email=credentials["credentials"]["email"],
            password=credentials["credentials"]["password"],
        )

        # create a request object for sign-in view
        factory = APIRequestFactory()
        request = factory.post(
            reverse("api-sign-in"),
            json.dumps(credentials),
            content_type="application/json",
        )

        # sign the user in with the request object and retrieve the token associated with the
        # signed-in user
        SignInView.as_view()(request)
        token_obj = Token.objects.get(user=user)

        # use APIClient and the token to request a password change
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="TOKEN " + f"{token_obj.key}")
        response = client.patch(
            reverse("api-change-pw"),
            {
                "credentials": {
                    "email": credentials["credentials"]["email"],
                    "password": credentials["credentials"]["password"],
                    "new_password": "",
                    "new_password_confirmed": "",
                }
            },
            format="json",
        )

        # test assertions
        assert response.status_code == 400
        assert json.loads(response.content) == {
            "password_error": "No new passwords provided"
        }
