# ./account/serializers.py

from rest_framework.serializers import ModelSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class UserIdUsernameSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password", "email", "college", "major"]


class TokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class AccessTokenResponseSerializer(serializers.Serializer):
    access = serializers.CharField()


class MessageResponseSerializer(serializers.Serializer):
    detail = serializers.CharField()
