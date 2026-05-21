"""
Serializers for Brand model.
"""
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from apps.inventory.models import Brand
from apps.core.serializers import OrganizationListSerializer


class BrandListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for brand listings."""
    
    class Meta:
        model = Brand
        fields = ['id', 'code', 'name', 'country', 'is_active']


class BrandSerializer(serializers.ModelSerializer):
    """
    Full serializer for Brand model.
    """
    organization = OrganizationListSerializer(read_only=True)
    organization_id = serializers.IntegerField(write_only=True, required=False)
    
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = [
            'id', 'code', 'name', 'description',
            'country', 'website', 'is_active',
            'products_count',
            'organization', 'organization_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'organization', 'products_count',
            'created_at', 'updated_at'
        ]
    
    @extend_schema_field(serializers.IntegerField())
    def get_products_count(self, obj):
        """Get count of products using this brand."""
        return obj.products.count()
    
    def create(self, validated_data):
        """Create brand with organization from request user."""
        validated_data.pop('organization_id', None)
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update brand, ensuring organization doesn't change."""
        validated_data.pop('organization_id', None)
        return super().update(instance, validated_data)
