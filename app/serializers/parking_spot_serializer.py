from decimal import Decimal

from rest_framework import serializers

from utils.utils import is_integer

from ..models.parking_spot import ParkingSpot


class ParkingSpotSerializer(serializers.ModelSerializer):
    """
    Serializer for the parking spots model.

    lat / lng / rate:
        required fields

    created_at / updated_at:
        readonly fields
    """

    class Meta:
        model = ParkingSpot
        fields = [
            "id",
            "lat",
            "lng",
            "reserved",
            "active",
            "rate",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "id"]
        extra_kwargs = {
            "lat": {"required": True},
            "lng": {"required": True},
            "rate": {"required": True},
        }

    def validate_lat(self, value):
        """
        Must have upper and lower bounds of +90 and -90 respectively.
        The number of decimal places must be limited to 6.
        """

        if value > 90 or value < -90:
            raise serializers.ValidationError(
                "The lat must be between -90 on the "
                "Southern bound and +90 on the Northern bound, "
                "inclusively"
            )

        # # Multiply by 10^6 and check if result is an integer. If not, raise validation error.
        # if not is_integer(value * 10 ** 6):
        #     raise serializers.ValidationError(
        #         "The coordinate precision must be 6 decimals or less"
        #     )

        return value

    def validate_lng(self, value):
        """
        Must have upper and lower bounds of +180 and -180 respectively.
        The lower bound is exclusive and the upper bound is inclusive.
        The number of decimal places must be limited to 6.
        """

        # convert string to decimal
        decimal_lng = Decimal(value)

        if decimal_lng > 180 or decimal_lng <= -180:
            raise serializers.ValidationError(
                "The lng must be between exclusive -180 "
                "in the West, and inclusive +180 in the East"
            )

        if not is_integer(decimal_lng * 10 ** 6):
            raise serializers.ValidationError(
                "The coordinate precision must be 6 decimals or " "less"
            )

        return value

    def validate_rate(self, value):
        """
        Must have 2 decimals or less.
        Must be positive.
        """

        decimal_rate = Decimal(value)

        if value < 0:
            raise serializers.ValidationError(
                "The hour rate must be a positive number."
            )

        if not is_integer(decimal_rate * 10 ** 2):
            raise serializers.ValidationError(
                "The hourly rate must have no more than 2 " "decimals"
            )

        return value
