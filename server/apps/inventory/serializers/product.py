"""
Serializers for Product model.
"""
from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from apps.inventory.models import Product, Category, Brand, Unit
from apps.core.serializers import OrganizationListSerializer
from .category import CategoryListSerializer
from .brand import BrandListSerializer
from .unit import UnitListSerializer


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product listings."""
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True, allow_null=True)
    unit_name = serializers.CharField(source='unit.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'code', 'name', 'barcode',
            'product_type', 'category_name', 'brand_name', 'unit_name',
            'cost_price', 'selling_price', 'is_active'
        ]


class ProductSerializer(serializers.ModelSerializer):
    """
    Full serializer for Product model with nested relationships.
    """
    organization = OrganizationListSerializer(read_only=True)
    organization_id = serializers.IntegerField(write_only=True, required=False)
    
    # Write fields (ForeignKeys)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.none(),
        required=False,
        allow_null=True
    )
    brand = serializers.PrimaryKeyRelatedField(
        queryset=Brand.objects.none(),
        required=False,
        allow_null=True
    )
    unit = serializers.PrimaryKeyRelatedField(
        queryset=Unit.objects.none()
    )
    
    # Read fields (nested serializers)
    category_detail = CategoryListSerializer(source='category', read_only=True)
    brand_detail = BrandListSerializer(source='brand', read_only=True)
    unit_detail = UnitListSerializer(source='unit', read_only=True)
    
    # Computed fields
    total_stock = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'code', 'name', 'barcode', 'description',
            'product_type',
            'category', 'category_detail',
            'brand', 'brand_detail',
            'unit', 'unit_detail',
            'cost_price', 'selling_price',
            'reorder_level', 'reorder_quantity',
            'is_active', 'can_be_sold', 'can_be_purchased',
            'notes', 'total_stock',
            'organization', 'organization_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'organization',
            'category_detail', 'brand_detail', 'unit_detail',
            'total_stock', 'created_at', 'updated_at'
        ]
    
    def __init__(self, *args, **kwargs):
        """Set querysets based on request user's organization."""
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        
        if request and hasattr(request, 'user'):
            user = request.user
            if hasattr(user, 'organization') and user.organization:
                org = user.organization
                
                # Scope FK querysets to user's organization
                self.fields['category'].queryset = Category.objects.filter(
                    organization=org,
                    is_active=True
                )
                self.fields['brand'].queryset = Brand.objects.filter(
                    organization=org,
                    is_active=True
                )
                self.fields['unit'].queryset = Unit.objects.filter(
                    organization=org,
                    is_active=True
                )
    
    @extend_schema_field(serializers.FloatField())
    def get_total_stock(self, obj):
        """Get total stock across all warehouses."""
        from django.db.models import Sum
        total = obj.stock_records.aggregate(total=Sum('quantity'))['total']
        return float(total) if total else 0.0
    
    def validate(self, attrs):
        """
        Validate that all FK objects belong to same organization.
        """
        request = self.context.get('request')
        if request and hasattr(request.user, 'organization'):
            org = request.user.organization
            
            # Validate category
            if 'category' in attrs and attrs['category']:
                if attrs['category'].organization != org:
                    raise serializers.ValidationError({
                        'category': 'Category must belong to your organization.'
                    })
            
            # Validate brand
            if 'brand' in attrs and attrs['brand']:
                if attrs['brand'].organization != org:
                    raise serializers.ValidationError({
                        'brand': 'Brand must belong to your organization.'
                    })
            
            # Validate unit
            if 'unit' in attrs and attrs['unit']:
                if attrs['unit'].organization != org:
                    raise serializers.ValidationError({
                        'unit': 'Unit must belong to your organization.'
                    })
        
        return attrs
    
    def create(self, validated_data):
        """Create product with organization from request user."""
        validated_data.pop('organization_id', None)
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update product, ensuring organization doesn't change."""
        validated_data.pop('organization_id', None)
        return super().update(instance, validated_data)
