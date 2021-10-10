from decimal import Decimal

from rest_framework import serializers

from utils.utils import is_integer

from ..models.parking_spots import ParkingSpots


class ParkingSpotsSerializer(serializers.ModelSerializer):
    """
    Serializer for the parking spots model.

    longitude / latitude / rate:
        required fields

    created_at / updated_at:
        readonly fields
    """

    class Meta:
        model = ParkingSpots
        fields = [
            "latitude",
            "longitude",
            "reserved",
            "rate",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]
        extra_kwargs = {
            "latitude": {"required": True},
            "longitude": {"required": True},
            "rate": {"required": True},
        }

        def validate_latitude(self, latitude):
            """
            Must have upper and lower bounds of +90 and -90 respectively.
            The number of decimal places must be limited to 6.
            """

            # convert string to decimal
            decimal_latitude = Decimal(latitude)

            if decimal_latitude > 90 or decimal_latitude < -90:
                raise serializers.ValidationError(
                    "The latitude must be between -90 on the "
                    "Southern bound and +90 on the Northern bound, "
                    "inclusively"
                )

            # Multiply by 10^6 and check if result is an integer. If not, raise validation error.

            if not is_integer(decimal_latitude * 10 ^ 6):
                raise serializers.ValidationError(
                    "The coordinate precision must be 6 decimals or " "less"
                )

            return decimal_latitude

        def validate_longitude(self, longitude):
            """
            Must have upper and lower bounds of +180 and -180 respectively.
            The lower bound is exclusive and the upper bound is inclusive.
            The number of decimal places must be limited to 6.
            """

            # convert string to decimal
            decimal_longitude = Decimal(longitude)

            if decimal_longitude > 180 or decimal_longitude <= -180:
                raise serializers.ValidationError(
                    "The longitude must be between exclusive -180 "
                    "in the West, and inclusive +180 in the East"
                )

            if not is_integer(decimal_longitude * 10 ^ 6):
                raise serializers.ValidationError(
                    "The coordinate precision must be 6 decimals or " "less"
                )

            return decimal_longitude

        def validate_rate(self, rate):
            """
            Must have 2 decimals or less.
            Must be positive.
            """

            decimal_rate = Decimal(rate)

            if rate < 0:
                raise serializers.ValidationError(
                    "The hour rate must be a positive number."
                )

            if not is_integer(decimal_rate * 10 ^ 2):
                raise serializers.ValidationError(
                    "The hourly rate must have no more than 2 " "decimals"
                )

            return decimal_rate
