"""
Serializers for Role model.
"""
from rest_framework import serializers
from apps.core.models import Role, RolePermission, Organization
from apps.core.serializers.permission import PermissionListSerializer
from apps.core.serializers.organization import OrganizationListSerializer


class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer for Role model with organization handling.
    
    - organization_id: Write-only field for creating roles (required for super admin)
    - organization: Read-only field showing full organization details in response
    
    Organization assignment is validated in the view layer.
    """
    organization_id = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        source='organization',
        write_only=True,
        required=False  # Required only for super admin, validated in view
    )
    organization = OrganizationListSerializer(read_only=True)
    permissions = PermissionListSerializer(
        source='role_permissions.permission',
        many=True,
        read_only=True
    )
    users_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'organization_id', 'organization', 'description',
            'is_active', 'permissions', 'users_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'organization', 'created_at', 'updated_at', 'users_count']
    
    def get_users_count(self, obj):
        """Get count of users with this role."""
        return obj.users.count()


class RoleListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing roles.
    """
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'organization_name', 'is_active']
