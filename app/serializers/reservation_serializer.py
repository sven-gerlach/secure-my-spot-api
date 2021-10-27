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
        fields = ["user", "email", "parking_spot", "paid", "start_time", "end_time"]

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

        if bool(attrs.get("user")) == bool(attrs.get("email")):
            raise serializers.ValidationError(
                "Either a user instance or an email must be provided, but not both concurrently"
            )

        if attrs["end_time"] <= attrs["start_time"]:
            raise serializers.ValidationError(
                "The end_time must be strictly greater / later than the start_time"
            )

        return attrs
