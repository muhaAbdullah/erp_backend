"""
Serializers for Category model.
"""
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from apps.inventory.models import Category
from apps.core.serializers import OrganizationListSerializer


class CategoryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for category listings."""
    parent_name = serializers.CharField(source='parent.name', read_only=True, allow_null=True)
    
    class Meta:
        model = Category
        fields = ['id', 'code', 'name', 'parent', 'parent_name', 'is_active']


class CategorySerializer(serializers.ModelSerializer):
    """
    Full serializer for Category model with nested relationships.
    """
    organization = OrganizationListSerializer(read_only=True)
    organization_id = serializers.IntegerField(write_only=True, required=False)
    
    # Parent category (write)
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.none(),
        required=False,
        allow_null=True
    )
    
    # Parent category details (read)
    parent_detail = CategoryListSerializer(source='parent', read_only=True)
    
    # Computed fields
    full_path = serializers.CharField(source='get_full_path', read_only=True)
    children_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'code', 'name', 'description',
            'parent', 'parent_detail', 'full_path',
            'is_active', 'children_count',
            'organization', 'organization_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'organization', 'parent_detail', 'full_path',
            'children_count', 'created_at', 'updated_at'
        ]
    
    def __init__(self, *args, **kwargs):
        """Set querysets based on request user's organization."""
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        
        if request and hasattr(request, 'user'):
            user = request.user
            if hasattr(user, 'organization') and user.organization:
                # Scope parent queryset to user's organization
                self.fields['parent'].queryset = Category.objects.filter(
                    organization=user.organization,
                    is_active=True
                )
    
    @extend_schema_field(serializers.IntegerField())
    def get_children_count(self, obj):
        """Get count of child categories."""
        return obj.children.count()
    
    def validate(self, attrs):
        """
        Validate that parent category belongs to same organization.
        """
        request = self.context.get('request')
        if request and hasattr(request.user, 'organization'):
            org = request.user.organization
            
            # Validate parent belongs to same organization
            if 'parent' in attrs and attrs['parent']:
                if attrs['parent'].organization != org:
                    raise serializers.ValidationError({
                        'parent': 'Parent category must belong to your organization.'
                    })
        
        return attrs
    
    def create(self, validated_data):
        """Create category with organization from request user."""
        # Remove organization_id if present (handled by view)
        validated_data.pop('organization_id', None)
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update category, ensuring organization doesn't change."""
        # Remove organization_id if present
        validated_data.pop('organization_id', None)
        return super().update(instance, validated_data)
