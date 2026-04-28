"""
Serializers for Permission model.
"""
from rest_framework import serializers
from apps.core.models import Permission


class PermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for Permission model.
    """
    class Meta:
        model = Permission
        fields = ['id', 'name', 'permission_code', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PermissionListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing permissions.
    """
    class Meta:
        model = Permission
        fields = ['id', 'name', 'permission_code']
