"""
Serializer for AuditLog model.
"""
from rest_framework import serializers
from apps.core.models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    """
    Read-only serializer for audit logs.
    """
    user_email = serializers.EmailField(source='user.email', read_only=True, allow_null=True)
    user_name = serializers.CharField(source='user.username', read_only=True, allow_null=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True, allow_null=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = [
            'id',
            'user',
            'user_email',
            'user_name',
            'organization',
            'organization_name',
            'action',
            'action_display',
            'model_name',
            'object_id',
            'changes',
            'ip_address',
            'user_agent',
            'created_at'
        ]
        read_only_fields = fields  # All fields are read-only
