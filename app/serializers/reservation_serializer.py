"""
A module for reservation serializer class
"""

from django.contrib.auth import get_user_model
from django.db.models import ObjectDoesNotExist
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
            "start_time",
            "end_time",
            "paid",
            "stripe_payment_intent_id",
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
        instance.stripe_payment_intent_id = validated_data.get(
            "stripe_payment_intent_id", instance.stripe_payment_intent_id
        )
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
            if attrs.get("end_time"):
                if attrs["end_time"] < self.instance.start_time:
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

    def validate_email(self, email):
        """
        If user is not authenticated and the email provided with the email field has an associated
        user in the db, throw an error that lets the client know that this particular email has
        an associated account which ought to be used for the reservation instead
        """

        User = get_user_model()

        # only run validation if the user is not authenticated
        if not self.context["user"].is_authenticated:
            try:
                User.objects.get(email=email)
                raise serializers.ValidationError(
                    "This email has been assigned to an existing account. Please sign into that "
                    "account to reserve your spot or use a different email address."
                )
            except ObjectDoesNotExist:
                return email

        return email
