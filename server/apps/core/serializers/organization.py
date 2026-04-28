"""
Serializers for Organization model.
"""
from rest_framework import serializers
from apps.core.models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    """
    Serializer for Organization model.
    """
    users_count = serializers.SerializerMethodField()
    roles_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = ['id', 'name', 'description', 'is_active', 'users_count', 'roles_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'users_count', 'roles_count']
    
    def get_users_count(self, obj):
        """Get count of users in this organization."""
        return obj.users.count()
    
    def get_roles_count(self, obj):
        """Get count of roles in this organization."""
        return obj.roles.count()


class OrganizationListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing organizations.
    """
    class Meta:
        model = Organization
        fields = ['id', 'name', 'is_active']
