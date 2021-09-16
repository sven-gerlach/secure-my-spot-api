"""
Module for all User model related tests
Source for pytes-django:
https://djangostars.com/blog/django-pytest-testing/
"""

from django.contrib.auth import get_user_model

import pytest

# marking this module such that tests have access to the database
pytestmark = pytest.mark.django_db


def test_create_user():
    """ensure a newly created user is in the database"""
    User = get_user_model()
    user = User.objects.create_user(email="email@me.com", password="foo")
    assert User.objects.count() == 1
    assert user.email == "email@me.com"
    assert user.is_active is True


def test_create_superuser():
    """ensure a newly created superuser is in the database"""
    User = get_user_model()
    admin_user = User.objects.create_superuser(email="super@user.de", password="foo")
    assert admin_user.email == "super@user.de"
    assert admin_user.is_active is True
    assert admin_user.is_staff is True
    assert admin_user.is_superuser is True
