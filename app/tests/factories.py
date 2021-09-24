import factory
from faker import Faker

from ..models.user_model import User


class UserFactory(factory.django.DjangoModelFactory):
    """
    Factory that generates a user with a random email and random password
    UserFactory must subclass django ORM DjangoModelFactory for UserFactory.create() to create an
    instance of a new user on the db
    Source: https://pypi.org/project/factory-boy/
    """

    class Meta:
        model = User

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
