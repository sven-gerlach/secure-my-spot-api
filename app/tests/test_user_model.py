"""
Module for all User model related tests
Source for pytes-django:
https://djangostars.com/blog/django-pytest-testing/
"""

import pytest
from django.contrib.auth import get_user_model

# marking this module such that tests have access to the database
pytestmark = pytest.mark.django_db


def test_create_user():
    """ensure a newly created user is in the database"""
    User = get_user_model()
    user = User.objects.create_user(email="email@email.com", password="foo")
    assert User.objects.count() == 1
    assert user.email == "email@email.com"
    assert user.is_active is True


def test_create_invalid_user():
    """test creating invalid user yields ValueError"""
    User = get_user_model()
    with pytest.raises(
        ValueError, match="New users must provide a valid email and password"
    ):
        User.objects.create_user(email="", password="foo")
    with pytest.raises(
        ValueError, match="New users must provide a valid email and password"
    ):
        User.objects.create_user(email="email@email.com", password="")


def test_create_superuser():
    """ensure a newly created superuser is in the database"""
    User = get_user_model()
    admin_user = User.objects.create_superuser(email="super@user.de", password="foo")
    assert admin_user.email == "super@user.de"
    assert admin_user.is_active is True
    assert admin_user.is_staff is True
    assert admin_user.is_superuser is True


def test_create_invalid_superuser():
    """test creating invalid superuser yields ValueError"""
    User = get_user_model()
    with pytest.raises(
        ValueError, match="New superusers must provide a valid email and password"
    ):
        User.objects.create_superuser(email="", password="foo")
    with pytest.raises(
        ValueError, match="New superusers must provide a valid email and password"
    ):
        User.objects.create_superuser(email="email@email.com", password="")


def test_string_rep():
    """String representation of user object should return email"""
    User = get_user_model()
    user = User.objects.create_user(email="user@email.de", password="foo")
    assert user.__str__() == user.email


def test_get_full_name():
    """test get_full_name returns correct name and surname"""
    User = get_user_model()
    user = User.objects.create_user(email="user@email.de", password="foo")
    user.name = "name"
    user.surname = "surname"
    assert user.get_full_name() == "name surname"


def test_get_short_name():
    """get_short_name returns user's name"""
    User = get_user_model()
    user = User.objects.create_user(email="user@email.de", password="foo")
    user.name = "name"
    user.surname = "surname"
    assert user.get_short_name() == "name"
