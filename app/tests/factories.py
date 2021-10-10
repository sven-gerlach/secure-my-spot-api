import factory
from faker import Factory, Faker

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

    latitude = faker.pydecimal(right_digits=6, min_value=-90, max_value=90)
    longitude = faker.pydecimal(right_digits=6, min_value=-179.999999, max_value=180)
    rate = faker.pydecimal(right_digits=2, min_value=10, max_value=70)
