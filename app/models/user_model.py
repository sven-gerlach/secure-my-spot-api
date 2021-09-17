"""
Instead of user django's auth.User model it is highly recommended to create a
custom user model that affords the developer additional flexibility with regards
to field choices.

Ensure that AUTH_USER_MODEL in settings points to this module.

Sources:
https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#substituting-a-custom-user-model
https://testdriven.io/blog/django-custom-user-model/
"""

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifier for
    authentication. It needs to define the create_user and create_superuser
    methods.
    """

    def create_user(self, email, password):
        """
        Create and save a User with the given email and password.
        """
        if not email or not password:
            raise ValueError("New users must provide a valid email and password")

        # changes all characters to small caps
        email = self.normalize_email(email)

        # by default this refers to the user model (presumably as per
        # AUTH_USER_MODEL in settings?
        # Source: https://stackoverflow.com/questions/51163088/self-model-in-django-custom
        # -usermanager#51163172
        user = self.model(email=email)

        # create hash of password and set hashed pswd as field name
        user.set_password(password)

        # save new user in db and return user object
        user.save()
        return user

    def create_superuser(self, email, password):
        """
        Create and save a SuperUser with the given email and password.
        """
        if not email or not password:
            raise ValueError("New superusers must provide a valid email and password")

        user = self.create_user(email, password)

        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user


# Use PermissionsMixin to give custom User class
# access to all of Django's permissions framework
# Source:https://docs.djangoproject.com/en/3.0/topics/auth/customizing/#custom-users-and-permissions
class User(AbstractBaseUser, PermissionsMixin):
    """
    A user model that sub-classes the AbstractBaseUser class. This allows for
    ultimate freedom to define fields beyond the ones defined by the
    AbstractUser class.
    """

    # todo: improve email validation
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=50, blank=True)
    surname = models.CharField(max_length=50, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    # todo: define token field?

    USERNAME_FIELD = "email"

    # objects needs to point to the customer user manager
    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_full_name(self):
        """Return the full name in string format. Appears alongside the username
        in an object’s history in django.contrib.admin"""
        return f"{self.name} {self.surname}"

    def get_short_name(self):
        """Returns the first name. Replaces the username in the greeting to the
        user in the header of django.contrib.admin"""
        return f"{self.name}"
