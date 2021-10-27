"""
Implement customised form fields for the parking spots model to ensure validation
"""

from django import forms
from django.forms import ModelForm

from ..models.parking_spot import ParkingSpot


class CustomParkingSpotForm(ModelForm):
    """
    Set implicit model field validation for latitude, longitude, and rate
    """

    lat = forms.DecimalField(
        max_value=90,
        min_value=-90,
        decimal_places=6,
        required=True,
        help_text="GPS latitude bounded by [-90,90] and with 6 decimals",
    )

    lng = forms.DecimalField(
        max_value=180,
        min_value=-179.999999,
        decimal_places=6,
        required=True,
        help_text="GPS longitude bounded by (-180, 180] with 6 decimals",
    )

    rate = forms.DecimalField(
        min_value=0,
        decimal_places=2,
        required=True,
        help_text="Specifies if the parking spot is already reserved",
    )

    class Meta:
        model = ParkingSpot
        fields = ("lat", "lng", "rate", "reserved", "active")
