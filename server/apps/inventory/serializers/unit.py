"""
Serializers for Unit model.
"""
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from apps.inventory.models import Unit
from apps.core.serializers import OrganizationListSerializer


class UnitListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for unit listings."""
    
    class Meta:
        model = Unit
        fields = ['id', 'code', 'name', 'symbol', 'is_active']


class UnitSerializer(serializers.ModelSerializer):
    """
    Full serializer for Unit model.
    """
    organization = OrganizationListSerializer(read_only=True)
    organization_id = serializers.IntegerField(write_only=True, required=False)
    
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Unit
        fields = [
            'id', 'code', 'name', 'symbol', 'description',
            'is_active', 'products_count',
            'organization', 'organization_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'organization', 'products_count',
            'created_at', 'updated_at'
        ]
    
    @extend_schema_field(serializers.IntegerField())
    def get_products_count(self, obj):
        """Get count of products using this unit."""
        return obj.products.count()
    
    def create(self, validated_data):
        """Create unit with organization from request user."""
        validated_data.pop('organization_id', None)
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update unit, ensuring organization doesn't change."""
        validated_data.pop('organization_id', None)
        return super().update(instance, validated_data)
