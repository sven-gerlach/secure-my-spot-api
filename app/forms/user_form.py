from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from ..models.user_model import User


class CustomUserCreationForm(UserCreationForm):
    """A custom form with bespoke form fields"""

    class Meta:
        model = User
        fields = ('email', 'name', 'surname', 'is_staff', 'is_superuser', 'is_active')


class CustomerUserChangeForm(UserChangeForm):
    """A custom form with bespoke form fields"""

    class Meta:
        model = User
        fields = ('email', 'name', 'surname', 'is_staff', 'is_superuser', 'is_active')
