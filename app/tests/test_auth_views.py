"""
Module for all User model related tests
"""

import json

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIRequestFactory

from ..models.user_model import User
from ..views.auth_views import SignUpView

# marking this module such that tests have access to the database
pytestmark = pytest.mark.django_db


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
