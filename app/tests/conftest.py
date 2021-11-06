"""
This module is being loaded automatically by Pytest. It includes all fixtures which are also
automatically loaded in any test suites that require them. Therefore, fixtures can be used in any
test function without the need for importing the fixture into the module.
"""

from datetime import datetime, timedelta, timezone

import pytest
from faker import Faker
from model_bakery import baker
from rest_framework.test import APIClient

from ..models.reservation import Reservation
from ..models.user import User
from .factories import ParkingSpotFactory

# instantiate faker instance
fake = Faker()


@pytest.fixture
def user():
    """
    Fixture function for a user instance
    """

    return baker.make(User)


@pytest.fixture
def parking_spot():
    """
    A fixture function that creates on the db and returns a clean random parking spot instance in
    form of a django query object.
    """

    # create a parking spot instance and save it on the db
    return ParkingSpotFactory()


@pytest.fixture
def reservation_unauth_user():
    """
    Create and return a reservation instance in form of a django query object. Note: this instance
    does not include a reference to a user instance. It does include a reference to a parking spot
    ref. The reservation, and by extension the parking spot instance has been created on the db
    automatically with the help of  model_bakery.
    """

    start_time = datetime.now(tz=timezone.utc)
    end_time = start_time + timedelta(minutes=10)

    return baker.make(Reservation, start_time=start_time, end_time=end_time)


@pytest.fixture
def reservation_auth_user():
    """
    Create and return a reservation instance with a ref key to a user and parking spot instance.
    The email field on the reservation instance is ensured to be the same as the email field on
    the user instance.
    """
    email = fake.ascii_email()
    start_time = datetime.now(tz=timezone.utc)
    end_time = start_time + timedelta(minutes=10)
    rate = fake.pydecimal(left_digits=2, right_digits=2, positive=True)

    return baker.make(
        Reservation,
        rate=rate,
        parking_spot__rate=rate,
        start_time=start_time,
        end_time=end_time,
        _fill_optional=True,
        email=email,
        user__email=email,
    )


@pytest.fixture
def client():
    """
    Returns the APIClient which, when invoked, returns the view's response object
    """
    return APIClient()
