from rest_framework import serializers
from .models import FriendRequest
from user.serializers import UserSerializer

class FriendRequestSendSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['to_user_id']

class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = UserSerializer(read_only=True)
    to_user = UserSerializer(read_only=True)

    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'status', 'timestamp']

class FriendRequestActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ['status']
