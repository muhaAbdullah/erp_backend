"""
Serializers for Stock models.
"""
from rest_framework import serializers
from django.db import transaction
from apps.inventory.models import (
    ProductStock, StockMovement, StockTransfer, StockTransferItem,
    StockAdjustment, StockAdjustmentItem, Product, Warehouse
)
from apps.core.serializers import OrganizationListSerializer
from .product import ProductListSerializer
from .warehouse import WarehouseListSerializer


# ==================== ProductStock Serializers ====================

class ProductStockListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for stock listings."""
    product_code = serializers.CharField(source='product.code', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    warehouse_code = serializers.CharField(source='warehouse.code', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    available_quantity = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = ProductStock
        fields = [
            'id', 'product', 'product_code', 'product_name',
            'warehouse', 'warehouse_code', 'warehouse_name',
            'quantity', 'reserved_quantity', 'available_quantity'
        ]


class ProductStockSerializer(serializers.ModelSerializer):
    """Full serializer for ProductStock model."""
    organization = OrganizationListSerializer(read_only=True)
    organization_id = serializers.IntegerField(write_only=True, required=False)
    
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.none())
    warehouse = serializers.PrimaryKeyRelatedField(queryset=Warehouse.objects.none())
    
    product_detail = ProductListSerializer(source='product', read_only=True)
    warehouse_detail = WarehouseListSerializer(source='warehouse', read_only=True)
    
    available_quantity = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = ProductStock
        fields = [
            'id', 'product', 'product_detail',
            'warehouse', 'warehouse_detail',
            'quantity', 'reserved_quantity', 'available_quantity',
            'organization', 'organization_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'organization', 'product_detail', 'warehouse_detail',
            'available_quantity', 'created_at', 'updated_at'
        ]
    
    def __init__(self, *args, **kwargs):
        """Set querysets based on request user's organization."""
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        
        if request and hasattr(request, 'user'):
            user = request.user
            if hasattr(user, 'organization') and user.organization:
                org = user.organization
                self.fields['product'].queryset = Product.objects.filter(
                    organization=org, is_active=True
                )
                self.fields['warehouse'].queryset = Warehouse.objects.filter(
                    organization=org, is_active=True
                )
    
    def validate(self, attrs):
        """Validate FK objects belong to same organization."""
        request = self.context.get('request')
        if request and hasattr(request.user, 'organization'):
            org = request.user.organization
            
            if 'product' in attrs and attrs['product'].organization != org:
                raise serializers.ValidationError({
                    'product': 'Product must belong to your organization.'
                })
            
            if 'warehouse' in attrs and attrs['warehouse'].organization != org:
                raise serializers.ValidationError({
                    'warehouse': 'Warehouse must belong to your organization.'
                })
        
        return attrs
    
    def create(self, validated_data):
        """Create stock record."""
        validated_data.pop('organization_id', None)
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update stock record."""
        validated_data.pop('organization_id', None)
        return super().update(instance, validated_data)


# ==================== StockMovement Serializers ====================

class StockMovementListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for movement listings."""
    product_code = serializers.CharField(source='product.code', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    warehouse_code = serializers.CharField(source='warehouse.code', read_only=True)
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'product_code', 'product_name', 'warehouse_code',
            'movement_type', 'movement_type_display',
            'quantity', 'balance_after', 'reference_number',
            'movement_date'
        ]


class StockMovementSerializer(serializers.ModelSerializer):
    """Full serializer for StockMovement model."""
    organization = OrganizationListSerializer(read_only=True)
    
    product_detail = ProductListSerializer(source='product', read_only=True)
    warehouse_detail = WarehouseListSerializer(source='warehouse', read_only=True)
    movement_type_display = serializers.CharField(source='get_movement_type_display', read_only=True)
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'product', 'product_detail',
            'warehouse', 'warehouse_detail',
            'movement_type', 'movement_type_display',
            'quantity', 'balance_after',
            'reference_type', 'reference_id', 'reference_number',
            'notes', 'movement_date',
            'organization', 'created_at'
        ]
        read_only_fields = [
            'id', 'organization', 'product_detail', 'warehouse_detail',
            'movement_type_display', 'movement_date', 'created_at'
        ]


# ==================== StockTransfer Serializers ====================

class StockTransferItemSerializer(serializers.ModelSerializer):
    """Serializer for StockTransferItem."""
    organization_id = serializers.IntegerField(write_only=True, required=False)
    
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.none())
    product_detail = ProductListSerializer(source='product', read_only=True)
    
    class Meta:
        model = StockTransferItem
        fields = [
            'id', 'product', 'product_detail',
            'quantity', 'notes',
            'organization_id'
        ]
        read_only_fields = ['id', 'product_detail']
    
    def __init__(self, *args, **kwargs):
        """Set querysets based on request user's organization."""
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        
        if request and hasattr(request, 'user'):
            user = request.user
            if hasattr(user, 'organization') and user.organization:
                self.fields['product'].queryset = Product.objects.filter(
                    organization=user.organization, is_active=True
                )


class StockTransferListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for transfer listings."""
    source_warehouse_name = serializers.CharField(source='source_warehouse.name', read_only=True)
    destination_warehouse_name = serializers.CharField(source='destination_warehouse.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = StockTransfer
        fields = [
            'id', 'transfer_number', 'transfer_date',
            'source_warehouse_name', 'destination_warehouse_name',
            'status', 'status_display'
        ]


class StockTransferSerializer(serializers.ModelSerializer):
    """Full serializer for StockTransfer model with nested items."""
    organization = OrganizationListSerializer(read_only=True)
    organization_id = serializers.IntegerField(write_only=True, required=False)
    
    source_warehouse = serializers.PrimaryKeyRelatedField(queryset=Warehouse.objects.none())
    destination_warehouse = serializers.PrimaryKeyRelatedField(queryset=Warehouse.objects.none())
    
    source_warehouse_detail = WarehouseListSerializer(source='source_warehouse', read_only=True)
    destination_warehouse_detail = WarehouseListSerializer(source='destination_warehouse', read_only=True)
    
    items = StockTransferItemSerializer(many=True, required=False)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = StockTransfer
        fields = [
            'id', 'transfer_number', 'transfer_date',
            'source_warehouse', 'source_warehouse_detail',
            'destination_warehouse', 'destination_warehouse_detail',
            'status', 'status_display', 'notes',
            'items', 'completed_at', 'completed_by',
            'organization', 'organization_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'organization', 'source_warehouse_detail',
            'destination_warehouse_detail', 'status_display',
            'completed_at', 'completed_by',
            'created_at', 'updated_at'
        ]
    
    def get_fields(self):
        """Override to set querysets based on request user's organization."""
        fields = super().get_fields()
        request = self.context.get('request')
        
        if request and hasattr(request, 'user'):
            user = request.user
            if hasattr(user, 'organization') and user.organization:
                org = user.organization
                # Set warehouse querysets
                if 'source_warehouse' in fields:
                    fields['source_warehouse'].queryset = Warehouse.objects.filter(
                        organization=org, is_active=True
                    )
                if 'destination_warehouse' in fields:
                    fields['destination_warehouse'].queryset = Warehouse.objects.filter(
                        organization=org, is_active=True
                    )
                # Set product queryset for nested item serializers
                if 'items' in fields and hasattr(fields['items'], 'child'):
                    fields['items'].child.fields['product'].queryset = Product.objects.filter(
                        organization=org, is_active=True
                    )
        
        return fields
    
    def validate(self, attrs):
        """Validate FK objects belong to same organization."""
        request = self.context.get('request')
        if request and hasattr(request.user, 'organization'):
            org = request.user.organization
            
            if 'source_warehouse' in attrs and attrs['source_warehouse'].organization != org:
                raise serializers.ValidationError({
                    'source_warehouse': 'Source warehouse must belong to your organization.'
                })
            
            if 'destination_warehouse' in attrs and attrs['destination_warehouse'].organization != org:
                raise serializers.ValidationError({
                    'destination_warehouse': 'Destination warehouse must belong to your organization.'
                })
        
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        """Create transfer with nested items."""
        items_data = validated_data.pop('items', [])
        validated_data.pop('organization_id', None)
        
        transfer = StockTransfer.objects.create(**validated_data)
        
        for item_data in items_data:
            item_data.pop('organization_id', None)
            StockTransferItem.objects.create(
                transfer=transfer,
                organization=transfer.organization,
                **item_data
            )
        
        return transfer
    
    @transaction.atomic
    def update(self, instance, validated_data):
        """Update transfer (items cannot be updated directly)."""
        validated_data.pop('organization_id', None)
        validated_data.pop('items', None)  # Items updated separately
        return super().update(instance, validated_data)


# ==================== StockAdjustment Serializers ====================

class StockAdjustmentItemSerializer(serializers.ModelSerializer):
    """Serializer for StockAdjustmentItem."""
    organization_id = serializers.IntegerField(write_only=True, required=False)
    
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.none())
    product_detail = ProductListSerializer(source='product', read_only=True)
    new_quantity = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = StockAdjustmentItem
        fields = [
            'id', 'product', 'product_detail',
            'quantity_change', 'current_quantity', 'new_quantity',
            'notes', 'organization_id'
        ]
        read_only_fields = ['id', 'product_detail', 'new_quantity']
    
    def __init__(self, *args, **kwargs):
        """Set querysets based on request user's organization."""
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        
        if request and hasattr(request, 'user'):
            user = request.user
            if hasattr(user, 'organization') and user.organization:
                self.fields['product'].queryset = Product.objects.filter(
                    organization=user.organization, is_active=True
                )


class StockAdjustmentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for adjustment listings."""
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = StockAdjustment
        fields = [
            'id', 'adjustment_number', 'adjustment_date',
            'warehouse_name', 'reason', 'reason_display',
            'status', 'status_display'
        ]


class StockAdjustmentSerializer(serializers.ModelSerializer):
    """Full serializer for StockAdjustment model with nested items."""
    organization = OrganizationListSerializer(read_only=True)
    organization_id = serializers.IntegerField(write_only=True, required=False)
    
    warehouse = serializers.PrimaryKeyRelatedField(queryset=Warehouse.objects.none())
    warehouse_detail = WarehouseListSerializer(source='warehouse', read_only=True)
    
    items = StockAdjustmentItemSerializer(many=True, required=False)
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = StockAdjustment
        fields = [
            'id', 'adjustment_number', 'adjustment_date',
            'warehouse', 'warehouse_detail',
            'reason', 'reason_display',
            'status', 'status_display', 'notes',
            'items', 'approved_at', 'approved_by',
            'organization', 'organization_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'organization', 'warehouse_detail',
            'reason_display', 'status_display',
            'approved_at', 'approved_by',
            'created_at', 'updated_at'
        ]
    
    def get_fields(self):
        """Override to set querysets based on request user's organization."""
        fields = super().get_fields()
        request = self.context.get('request')
        
        if request and hasattr(request, 'user'):
            user = request.user
            if hasattr(user, 'organization') and user.organization:
                org = user.organization
                # Set warehouse queryset
                if 'warehouse' in fields:
                    fields['warehouse'].queryset = Warehouse.objects.filter(
                        organization=org, is_active=True
                    )
                # Set product queryset for nested item serializers
                if 'items' in fields and hasattr(fields['items'], 'child'):
                    fields['items'].child.fields['product'].queryset = Product.objects.filter(
                        organization=org, is_active=True
                    )
        
        return fields
    
    def validate(self, attrs):
        """Validate FK objects belong to same organization."""
        request = self.context.get('request')
        if request and hasattr(request.user, 'organization'):
            org = request.user.organization
            
            if 'warehouse' in attrs and attrs['warehouse'].organization != org:
                raise serializers.ValidationError({
                    'warehouse': 'Warehouse must belong to your organization.'
                })
        
        return attrs
    
    @transaction.atomic
    def create(self, validated_data):
        """Create adjustment with nested items."""
        items_data = validated_data.pop('items', [])
        validated_data.pop('organization_id', None)
        
        adjustment = StockAdjustment.objects.create(**validated_data)
        
        for item_data in items_data:
            item_data.pop('organization_id', None)
            StockAdjustmentItem.objects.create(
                adjustment=adjustment,
                organization=adjustment.organization,
                **item_data
            )
        
        return adjustment
    
    @transaction.atomic
    def update(self, instance, validated_data):
        """Update adjustment (items cannot be updated directly)."""
        validated_data.pop('organization_id', None)
        validated_data.pop('items', None)  # Items updated separately
        return super().update(instance, validated_data)
