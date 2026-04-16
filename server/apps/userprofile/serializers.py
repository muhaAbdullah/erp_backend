from rest_framework import serializers
from .models import UserProfile
from django.db.models import Avg


class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    user_type = serializers.CharField(source='user.user_type', read_only=True)

    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

