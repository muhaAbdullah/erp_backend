from rest_framework import serializers
from .models import UserProfile
from django.db.models import Avg


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    user_type = serializers.CharField(source='user.user_type', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'first_name', 'last_name', 'image',
                  'username', 'email', 'user_type', 'created_at', 'updated_at']
        read_only_fields = ('user', 'username', 'email', 'user_type', 'created_at', 'updated_at')

