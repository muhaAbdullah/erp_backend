from rest_framework import serializers
from apps.core.models import Role, RolePermission, Organization, Permission
from apps.core.serializers.permission import PermissionListSerializer
from apps.core.serializers.organization import OrganizationListSerializer


class RoleSerializer(serializers.ModelSerializer):
    organization_id = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        source='organization',
        write_only=True,
        required=False
    )
    organization = OrganizationListSerializer(read_only=True)
    
    # FIX: use SerializerMethodField instead of source traversal across FK manager
    permissions = serializers.SerializerMethodField()
    
    users_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = [
            'id', 'name', 'organization_id', 'organization', 'description',
            'is_active', 'permissions', 'users_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'organization', 'created_at', 'updated_at', 'users_count']

    def get_permissions(self, obj):
        """Get all permissions assigned to this role."""
        perms = Permission.objects.filter(
            permission_roles__role=obj
        ).values('id', 'name', 'permission_code')
        return list(perms)

    def get_users_count(self, obj):
        return obj.users.count()


class RoleListSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name', read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'name', 'organization_name', 'is_active']