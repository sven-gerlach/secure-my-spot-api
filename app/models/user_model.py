"""
Instead of user django's auth.User model it is highly recommended to create a
custom user model that affords the developer additional flexibility with regards
to field choices.

Ensure that AUTH_USER_MODEL in settings points to this module.

Sources:
https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#substituting-a-custom-user-model
https://testdriven.io/blog/django-custom-user-model/

"""

from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    A user model that sub-classes the AbstractUser class.
    """
    pass
