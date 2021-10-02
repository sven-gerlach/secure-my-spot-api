"""
Serializers for relevant models
"""

from django.contrib.auth import authenticate
from rest_framework import serializers

from .models.user_model import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    class Meta:
        model = User
        fields = ["email", "password"]

    def create(self, validated_data):
        """implement custom create and update method or else the password is not saved as a hashed
        pw
        https://stackoverflow.com/questions/27586095/why-isnt-my-django-user-models-password-hashed
        """
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if attr == "password":
                instance.set_password(value)
            else:
                setattr(instance, attr, value)
        instance.save()
        return instance


class AuthTokenSerializer(serializers.Serializer):
    """
    Custom auth-token serializer class. This is necessary because the original
    AuthTokenSerializer class uses usernames. This newly implemented class, which sub-classes the
    same serializers.Serializer parent class, uses email instead of username.
    https://github.com/encode/django-rest-framework/blob/3.6.0/rest_framework/authtoken/serializers.py
    """

    email = serializers.CharField(label="e-Mail", write_only=True)
    password = serializers.CharField(
        label="Password",
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )
    token = serializers.CharField(label="Token", read_only=True)

    def validate(self, attrs):
        """Validate user"""
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"), email=email, password=password
            )

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = "Unable to log in with provided credentials."
                raise serializers.ValidationError(msg, code="authorization")
        else:
            msg = 'Must include "email" and "password".'
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = user
        return attrs
