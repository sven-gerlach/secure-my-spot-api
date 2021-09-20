"""
Custom user forms needed if a custom user model is implemented that doesn't use a username
Source: https://docs.djangoproject.com/en/3.2/topics/auth/customizing/#a-full-example
"""

from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from ..models.user_model import User


class CustomUserCreationForm(forms.ModelForm):
    """
    A custom form for a bespoke user model. Includes all the required fields, including a repeated
    password field.
    """

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ("email", "name", "surname", "is_staff", "is_superuser", "is_active")

    def clean_password2(self):
        """check that both passwords match"""
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        """Save provided password in hashed format"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class CustomerUserChangeForm(forms.ModelForm):
    """
    A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "name",
            "surname",
            "is_staff",
            "is_superuser",
            "is_active",
        )
