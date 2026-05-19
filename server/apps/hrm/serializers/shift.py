"""
Serializer for Shift model.
"""
from rest_framework import serializers
from apps.hrm.models import Shift
from apps.core.serializers import OrganizationListSerializer


class ShiftSerializer(serializers.ModelSerializer):
    """
    Serializer for Shift model with organization enforcement.
    Organization is auto-assigned from request user, excluded from create/update.
    """
    organization = OrganizationListSerializer(read_only=True)
    organization_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Shift
        fields = [
            'id', 'name', 'description', 'start_time', 'end_time', 'is_active',
            'organization', 'organization_id', 'code',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'organization', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Remove organization_id from validated_data as it's handled by mixin."""
        validated_data.pop('organization_id', None)
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Remove organization_id from validated_data to prevent changes."""
        validated_data.pop('organization_id', None)
        return super().update(instance, validated_data)
