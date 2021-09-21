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

# marking this module such that tests have access to the database
pytestmark = pytest.mark.django_db


# todo: reduce significant repetition in the test setups
def test_signupview():
    """Http response code should be 201 and data={"email": "[...]", "password": "[...]"}"""
    # request factory generates a request instance that can be used as the first argument in a view
    factory = APIRequestFactory()

    # https://www.django-rest-framework.org/api-guide/testing/#explicitly-encoding-the-request-body
    path = "/sign-up/"
    data = json.dumps(
        {
            "credentials": {
                "email": "test@test.com",
                "password": "secure",
                "password_confirmation": "secure",
            }
        }
    )
    content_type = "application/json"
    request = factory.post(path, data, content_type=content_type)

    # call the view with the request item
    response = SignUpView.as_view()(request)

    # test assertions
    assert response.status_code == 201
    assert json.loads(response.content) == {
        "email": "test@test.com",
        "password": "secure",
    }
    assert User.objects.count() == 1
    assert User.objects.last().email == "test@test.com"


def test_signupview_missing_email():
    """Missing email http response code of 400 and data for email=["This field is required."]"""
    # request factory generates a request instance that can be used as the first argument in a view
    factory = APIRequestFactory()

    # https://www.django-rest-framework.org/api-guide/testing/#explicitly-encoding-the-request-body
    path = "/sign-up/"
    data = json.dumps(
        {"credentials": {"password": "secure", "password_confirmation": "secure"}}
    )
    content_type = "application/json"
    request = factory.post(path, data, content_type=content_type)

    # call the view with the request item
    response = SignUpView.as_view()(request)

    # test assertions
    assert response.status_code == 400
    assert json.loads(response.content) == {"email": ["This field is required."]}


def test_signupview_blank_email():
    """Missing email http response code of 400 and data for email=["This field is required."]"""
    # request factory generates a request instance that can be used as the first argument in a view
    factory = APIRequestFactory()

    # https://www.django-rest-framework.org/api-guide/testing/#explicitly-encoding-the-request-body
    path = "/sign-up/"
    data = json.dumps(
        {
            "credentials": {
                "email": "",
                "password": "secure",
                "password_confirmation": "secure",
            }
        }
    )
    content_type = "application/json"
    request = factory.post(path, data, content_type=content_type)

    # call the view with the request item
    response = SignUpView.as_view()(request)

    # test assertions
    assert response.status_code == 400
    assert json.loads(response.content) == {"email": ["This field may not be blank."]}


def test_signupview_missing_password():
    """Missing email http response code of 400 and data for password=["This field is required."]"""
    # request factory generates a request instance that can be used as the first argument in a view
    factory = APIRequestFactory()

    # https://www.django-rest-framework.org/api-guide/testing/#explicitly-encoding-the-request-body
    path = "/sign-up/"
    data = json.dumps(
        {
            "credentials": {
                "email": "test@test.com",
            }
        }
    )
    content_type = "application/json"
    request = factory.post(path, data, content_type=content_type)

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
    path = "/sign-up/"
    data = json.dumps(
        {
            "credentials": {
                "email": "test@test.com",
                "password": "secured",
                "password_confirmation": "secure",
            }
        }
    )
    content_type = "application/json"
    request = factory.post(path, data, content_type=content_type)

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
    path = "/sign-up/"
    data = json.dumps(
        {
            "credentials": {
                "email": "test@test.com",
                "password": "secure",
                "password_confirmation": "secure",
            }
        }
    )
    content_type = "application/json"
    request = factory.post(path, data, content_type=content_type)

    # create a user in the database with the same credentials
    User = get_user_model()
    User.objects.create_user(email="test@test.com", password="secure")

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
    # create a user with an email and a stored password

    User = get_user_model()
    user = User.objects.create_user(email="test@test.de", password="secure enough?")

    # create a request object
    factory = APIRequestFactory()
    path = "/sign-in/"
    data = json.dumps(
        {"credentials": {"email": "test@test.de", "password": "secure enough?"}}
    )
    content_type = "application/json"
    request = factory.post(path, data, content_type=content_type)

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
    path = "/sign-in/"
    data = json.dumps(
        {"credentials": {"email": "test@test.de", "password": "secure enough?"}}
    )
    content_type = "application/json"
    request = factory.post(path, data, content_type=content_type)

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
    # create user
    User = get_user_model()
    User.objects.create_user(email="test@test.de", password="correct password")

    # create a request object
    factory = APIRequestFactory()
    path = "/sign-in/"
    data = json.dumps(
        {"credentials": {"email": "test@test.de", "password": "wrong password"}}
    )
    content_type = "application/json"
    request = factory.post(path, data, content_type=content_type)

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
