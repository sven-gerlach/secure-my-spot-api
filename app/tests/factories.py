import factory
from faker import Factory, Faker

from utils.utils import get_rand_decimal

from ..models.parking_spot import ParkingSpot
from ..models.user import User

# create
faker = Factory.create()


class UserFactory(factory.django.DjangoModelFactory):
    """
    Factory that generates a user with a random email and random password
    UserFactory must subclass django ORM DjangoModelFactory for UserFactory.create() to create an
    instance of a new user on the db
    Source: https://pypi.org/project/factory-boy/
    """

    class Meta:
        model = User

    # factory boy gives direct access to the Faker library through factory.Faker("identifier")
    email = factory.Faker("email")
    password = factory.Faker("password")


def get_json_credentials(email=None, password=None, password_confirmation=None):
    """Returns a python dictionary with user credentials"""
    fake = Faker()
    if email is None:
        email = fake.ascii_email()
    if password is None:
        password = fake.password()
    if password_confirmation is None:
        password_confirmation = password
    return {
        "credentials": {
            "email": f"{email}",
            "password": f"{password}",
            "password_confirmation": f"{password_confirmation}",
        }
    }


class ParkingSpotFactory(factory.django.DjangoModelFactory):
    """
    A factory that generates a new random parking spot
    """

    class Meta:
        model = ParkingSpot

    # Note: faker's algorithm for calculating a pydecimal returns the upper or lower bound when
    # the random decimal is above / below the upper/lower bound, thereby creating mostly lower or
    # upper bound results. Hence, a manual random Decimal number generator his being used.

    latitude = get_rand_decimal(min=-90, max=90, right_digits=6)

    longitude = get_rand_decimal(min=-179.999999, max=180, right_digits=6)

    rate = get_rand_decimal(min=0, max=100, right_digits=2)
