"""
Serializers for RolePermission model.
"""
from rest_framework import serializers
from apps.core.models import RolePermission, Role, Permission


class RolePermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for RolePermission model.
    """
    role_name = serializers.CharField(source='role.name', read_only=True)
    permission_name = serializers.CharField(source='permission.name', read_only=True)
    permission_code = serializers.CharField(source='permission.permission_code', read_only=True)
    
    class Meta:
        model = RolePermission
        fields = [
            'id', 'role', 'role_name', 'permission', 'permission_name', 
            'permission_code', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AssignPermissionSerializer(serializers.Serializer):
    """
    Serializer for assigning permissions to a role.
    """
    role_id = serializers.IntegerField(required=True)
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True,
        help_text="List of permission IDs to assign to the role"
    )
    
    def validate_role_id(self, value):
        """Validate that role exists."""
        try:
            Role.objects.get(id=value)
        except Role.DoesNotExist:
            raise serializers.ValidationError("Role does not exist")
        return value
    
    def validate_permission_ids(self, value):
        """Validate that all permissions exist."""
        if not value:
            raise serializers.ValidationError("At least one permission is required")
        
        existing_count = Permission.objects.filter(id__in=value).count()
        if existing_count != len(value):
            raise serializers.ValidationError("One or more permissions do not exist")
        
        return value
