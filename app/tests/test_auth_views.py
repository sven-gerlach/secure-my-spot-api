"""
Module for all User model related tests
"""

import json

import pytest
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory

from ..models.user_model import User
from ..views.auth_views import SignInView, SignUpView
from .factories import get_json_credentials

# marking this module such that tests have access to the database
pytestmark = pytest.mark.django_db


def test_signupview():
    """Http response code should be 201 and data={"email": "[...]", "password": "[...]"}"""
    # request factory generates a request instance that can be used as the first argument in a view
    factory = APIRequestFactory()

    # https://www.django-rest-framework.org/api-guide/testing/#explicitly-encoding-the-request-body
    credentials = get_json_credentials()
    request = factory.post(
        "/sign-up/", json.dumps(credentials), content_type="application/json"
    )

    # call the view with the request item
    response = SignUpView.as_view()(request)

    # test assertions
    assert response.status_code == 201
    assert json.loads(response.content) == {
        "email": credentials["credentials"]["email"],
        "password": credentials["credentials"]["password"],
    }
    assert User.objects.count() == 1
    assert User.objects.last().email == credentials["credentials"]["email"]


def test_signupview_missing_email():
    """Missing email http response code of 400 and data for email=["This field is required."]"""
    # request factory generates a request instance that can be used as the first argument in a view
    factory = APIRequestFactory()

    # https://www.django-rest-framework.org/api-guide/testing/#explicitly-encoding-the-request-body
    credentials = get_json_credentials()
    # remove email from credentials
    credentials["credentials"].pop("email", None)
    request = factory.post(
        "/sign-up/", json.dumps(credentials), content_type="application/json"
    )

    # call the view with the request item
    response = SignUpView.as_view()(request)
    # response.render()

    # test assertions
    assert response.status_code == 400
    assert json.loads(response.content) == {"email": ["This field is required."]}


def test_signupview_blank_email():
    """Missing email http response code of 400 and data for email=["This field is required."]"""
    """Missing email http response code of 400 and data for email=["This field is required."]"""
    # request factory generates a request instance that can be used as the first argument in a view
    factory = APIRequestFactory()

    # https://www.django-rest-framework.org/api-guide/testing/#explicitly-encoding-the-request-body
    credentials = get_json_credentials(email="")
    request = factory.post(
        "/sign-up/", json.dumps(credentials), content_type="application/json"
    )

    # call the view with the request item
    response = SignUpView.as_view()(request)
    # response.render()

    # test assertions
    assert response.status_code == 400
    assert json.loads(response.content) == {"email": ["This field may not be blank."]}


def test_signupview_missing_password():
    """Missing email http response code of 400 and data for password=["This field is required."]"""
    # request factory generates a request instance that can be used as the first argument in a view
    factory = APIRequestFactory()

    # https://www.django-rest-framework.org/api-guide/testing/#explicitly-encoding-the-request-body
    credentials = get_json_credentials()
    # remove password from credentials
    credentials["credentials"].pop("password", None)
    credentials["credentials"].pop("password_confirmation", None)
    request = factory.post(
        "/sign-up/", json.dumps(credentials), content_type="application/json"
    )

    # call the view with the request item
    response = SignUpView.as_view()(request)

    # test assertions
    assert response.status_code == 400
    assert json.loads(response.content) == {"password": ["This field is required."]}


def test_signupview_non_matching_passwords():
    """Missing email http response code of 400 and data [...]"""
    # request factory generates a request instance that can be used as the first argument in a view
    factory = APIRequestFactory()

    # https://www.django-rest-framework.org/api-guide/testing/#explicitly-encoding-the-request-body
    credentials = get_json_credentials(
        password_confirmation="wrong password confirmation"
    )
    request = factory.post(
        "/sign-up/", json.dumps(credentials), content_type="application/json"
    )

    # call the view with the request item
    response = SignUpView.as_view()(request)

    # test assertions
    assert response.status_code == 400
    assert json.loads(response.content) == {"password": ["Passwords don't match."]}


def test_signupview_user_already_exists():
    """Missing email http response code of 400 and data for email=["user with this email
    address already exists."]"""
    # request factory generates a request instance that can be used as the first argument in a view
    factory = APIRequestFactory()

    # https://www.django-rest-framework.org/api-guide/testing/#explicitly-encoding-the-request-body
    credentials = get_json_credentials()
    request = factory.post(
        "/sign-up/", json.dumps(credentials), content_type="application/json"
    )

    # create a user in the database with the same credentials
    User = get_user_model()
    User.objects.create_user(
        email=credentials["credentials"]["email"],
        password=credentials["credentials"]["password"],
    )

    # call the sign-up view with the request item
    response = SignUpView.as_view()(request)

    # test assertions
    assert response.status_code == 400
    assert json.loads(response.content) == {
        "email": ["user with this email address already exists."]
    }


def test_signinview():
    """Validate that token is stored in database on user object, http code is 201, and that the
    same token is successfully returned to the client {"token": "[...]"}"""
    # create credentials
    credentials = get_json_credentials()
    # credentials["credentials"].pop("email_confirmation", None)

    # create a user with credentials
    user = User.objects.create_user(
        email=credentials["credentials"]["email"],
        password=credentials["credentials"]["password"],
    )

    # create a request object
    factory = APIRequestFactory()
    request = factory.post(
        "/sign-in/", json.dumps(credentials), content_type="application/json"
    )

    # retrieve the response object by calling the view function with the request objects
    response = SignInView.as_view()(request)

    # test assertions
    assert response.status_code == 201
    assert json.loads(response.content) == {
        "token": Token.objects.get(user=user).key,
        "user_id": user.pk,
        "email": user.email,
    }


def test_signinview_email_does_not_exist():
    """Return error message to user with http code 404 and message {"email": ["This user does
    not exist."]}"""
    # create a request object
    factory = APIRequestFactory()
    credentials = get_json_credentials()
    request = factory.post(
        "/sign-in/", json.dumps(credentials), content_type="application/json"
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


def test_signinview_incorrect_password():
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

    # create a request object
    factory = APIRequestFactory()
    credentials["credentials"]["password"] = "wrong password"
    request = factory.post(
        "/sign-in/", json.dumps(credentials), content_type="application/json"
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