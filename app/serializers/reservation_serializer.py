"""
A module for reservation serializer class
"""

from rest_framework import serializers

from ..models.reservation import Reservation


class ReservationSerializer(serializers.ModelSerializer):
    """
    A serializer for the reservation model.
    """

    class Meta:
        model = Reservation
        fields = [
            "id",
            "user",
            "email",
            "parking_spot",
            "rate",
            "paid",
            "start_time",
            "end_time",
        ]

    def create(self, validated_data):
        """
        Create a new reservation resource
        """
        return Reservation.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Only the boolean field type "paid" and the end_time of the reservation period can be updated
        """
        instance.paid = validated_data.get("paid", instance.paid)
        instance.end_time = validated_data.get("end_time", instance.end_time)
        instance.save()
        return instance

    def validate(self, attrs):
        """
        Either user model instance or email must be provided but not both.
        end_time must be strictly greater / after start_time
        """

        # in a partial update the start_time property is not provided as only the end_time or the
        # paid fields may be updated. In case of a partial update, compare the end_time to the
        # instance value associated with start_time instead
        if attrs.get("start_time"):
            if attrs["end_time"] <= attrs["start_time"]:
                raise serializers.ValidationError(
                    "The end_time must be strictly greater / later than the start_time"
                )
        else:
            if attrs["end_time"] <= self.instance.start_time:
                raise serializers.ValidationError(
                    "The end_time must be strictly greater / later than the start_time"
                )

        return attrs

    def validate_parking_spot(self, parking_spot):
        """
        The parking spot must be active and available
        """

        if not parking_spot.active:
            raise serializers.ValidationError(
                "This parking spot is currently not commercially available"
            )

        if parking_spot.reserved:
            raise serializers.ValidationError("This parking spot is already reserved")

        return parking_spot
