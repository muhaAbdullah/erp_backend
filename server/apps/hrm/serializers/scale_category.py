"""
Serializer for ScaleCategory model.
"""
from rest_framework import serializers
from apps.hrm.models import ScaleCategory
from apps.core.serializers import OrganizationListSerializer


class ScaleCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for ScaleCategory model with organization enforcement.
    Organization is auto-assigned from request user, excluded from create/update.
    """
    organization = OrganizationListSerializer(read_only=True)
    organization_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = ScaleCategory
        fields = [
            'id', 'name', 'description', 'is_active',
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
