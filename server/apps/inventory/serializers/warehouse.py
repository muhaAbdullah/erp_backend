"""
Serializers for Warehouse model.
"""
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from apps.inventory.models import Warehouse
from apps.core.serializers import OrganizationListSerializer


class WarehouseListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for warehouse listings."""
    
    class Meta:
        model = Warehouse
        fields = ['id', 'code', 'name', 'city', 'is_active']


class WarehouseSerializer(serializers.ModelSerializer):
    """
    Full serializer for Warehouse model.
    """
    organization = OrganizationListSerializer(read_only=True)
    organization_id = serializers.IntegerField(write_only=True, required=False)
    
    stock_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Warehouse
        fields = [
            'id', 'code', 'name',
            'address', 'city', 'state', 'country', 'postal_code',
            'phone', 'email', 'is_active',
            'stock_count',
            'organization', 'organization_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'organization', 'stock_count',
            'created_at', 'updated_at'
        ]
    
    @extend_schema_field(serializers.IntegerField())
    def get_stock_count(self, obj):
        """Get count of stock records in this warehouse."""
        return obj.stock_records.count()
    
    def create(self, validated_data):
        """Create warehouse with organization from request user."""
        validated_data.pop('organization_id', None)
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update warehouse, ensuring organization doesn't change."""
        validated_data.pop('organization_id', None)
        return super().update(instance, validated_data)
