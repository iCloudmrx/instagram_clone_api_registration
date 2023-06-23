from django.core.validators import MinLengthValidator, MaxLengthValidator
from rest_framework import serializers
from . import models

from users.models import User

class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)


    class Meta:
        model = User
        fields = ['id', 'username', 'photo']


class ChatRoomSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    receiver = UserSerializer(read_only=True)
    created = serializers.DateTimeField(read_only=True)

    class Meta:
        model = models.ChatRoom
        fields = ['id', 'sender', 'receiver', 'message', 'created', 'updated']