"""
Serializer for the user model
"""

from rest_framework import serializers

from app.models.user import User


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
