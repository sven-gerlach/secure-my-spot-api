"""
Serializers for relevant models
"""

from rest_framework import serializers

from .models.user_model import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    class Meta:
        model = User
        fields = ["email", "password"]
