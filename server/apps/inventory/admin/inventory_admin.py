"""
Django Admin configuration for Inventory models.
"""
from django.contrib import admin
from apps.inventory.models import (
    Category, Brand, Unit, Warehouse, Product,
    ProductStock, StockMovement, StockTransfer, StockTransferItem,
    StockAdjustment, StockAdjustmentItem
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category model."""
    list_display = ['id', 'code', 'name', 'parent', 'is_active', 'organization', 'created_at']
    list_filter = ['is_active', 'organization', 'created_at']
    search_fields = ['code', 'name', 'description']
    ordering = ['organization', 'name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'code', 'name', 'description')
        }),
        ('Hierarchy', {
            'fields': ('parent',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Admin configuration for Brand model."""
    list_display = ['id','code', 'name', 'country', 'is_active', 'organization', 'created_at']
    list_filter = ['is_active', 'country', 'organization', 'created_at']
    search_fields = ['code', 'name', 'description']
    ordering = ['organization', 'name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    """Admin configuration for Unit model."""
    list_display = ['id','code', 'name', 'symbol', 'is_active', 'organization', 'created_at']
    list_filter = ['is_active', 'organization', 'created_at']
    search_fields = ['code', 'name', 'symbol']
    ordering = ['organization', 'name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    """Admin configuration for Warehouse model."""
    list_display = ['id','code', 'name', 'city', 'state', 'country', 'is_active', 'organization', 'created_at']
    list_filter = ['is_active', 'city', 'state', 'country', 'organization', 'created_at']
    search_fields = ['code', 'name', 'address', 'city']
    ordering = ['organization', 'name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'code', 'name')
        }),
        ('Address', {
            'fields': ('address', 'city', 'state', 'country', 'postal_code')
        }),
        ('Contact', {
            'fields': ('phone', 'email')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for Product model."""
    list_display = ['id',
        'code', 'name', 'product_type', 'category', 'brand', 'unit',
        'cost_price', 'selling_price', 'is_active', 'organization', 'created_at'
    ]
    list_filter = [
        'product_type', 'is_active', 'can_be_sold', 'can_be_purchased',
        'category', 'brand', 'organization', 'created_at'
    ]
    search_fields = ['code', 'name', 'barcode', 'description']
    ordering = ['organization', 'name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'code', 'name', 'barcode', 'description', 'product_type')
        }),
        ('Classification', {
            'fields': ('category', 'brand', 'unit')
        }),
        ('Pricing', {
            'fields': ('cost_price', 'selling_price')
        }),
        ('Stock Management', {
            'fields': ('reorder_level', 'reorder_quantity')
        }),
        ('Status', {
            'fields': ('is_active', 'can_be_sold', 'can_be_purchased')
        }),
        ('Additional', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProductStock)
class ProductStockAdmin(admin.ModelAdmin):
    """Admin configuration for ProductStock model."""
    list_display = ['id',
        'product', 'warehouse', 'quantity', 'reserved_quantity',
        'available_quantity', 'organization', 'updated_at'
    ]
    list_filter = ['warehouse', 'organization', 'created_at']
    search_fields = ['product__code', 'product__name', 'warehouse__code', 'warehouse__name']
    ordering = ['organization', 'warehouse', 'product']
    readonly_fields = ['created_at', 'updated_at']
    
    def available_quantity(self, obj):
        """Display available quantity."""
        return obj.available_quantity
    available_quantity.short_description = 'Available Qty'


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    """Admin configuration for StockMovement model."""
    list_display = ['id',
        'product', 'warehouse', 'movement_type', 'quantity',
        'balance_after', 'reference_number', 'movement_date', 'organization'
    ]
    list_filter = ['movement_type', 'warehouse', 'organization', 'movement_date']
    search_fields = [
        'product__code', 'product__name', 'reference_number',
        'warehouse__code', 'warehouse__name'
    ]
    ordering = ['-movement_date']
    readonly_fields = ['movement_date', 'created_at']
    
    # Make movements read-only (immutable)
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


class StockTransferItemInline(admin.TabularInline):
    """Inline admin for StockTransferItem."""
    model = StockTransferItem
    extra = 1
    fields = ['product', 'quantity', 'notes']


@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    """Admin configuration for StockTransfer model."""
    list_display = ['id',
        'transfer_number', 'source_warehouse', 'destination_warehouse',
        'transfer_date', 'status', 'organization', 'created_at'
    ]
    list_filter = ['status', 'source_warehouse', 'destination_warehouse', 'organization', 'transfer_date']
    search_fields = ['transfer_number', 'notes']
    ordering = ['-transfer_date']
    readonly_fields = ['completed_at', 'completed_by', 'created_at', 'updated_at']
    inlines = [StockTransferItemInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'transfer_number', 'transfer_date')
        }),
        ('Warehouses', {
            'fields': ('source_warehouse', 'destination_warehouse')
        }),
        ('Status', {
            'fields': ('status', 'notes')
        }),
        ('Completion', {
            'fields': ('completed_at', 'completed_by'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class StockAdjustmentItemInline(admin.TabularInline):
    """Inline admin for StockAdjustmentItem."""
    model = StockAdjustmentItem
    extra = 1
    fields = ['product', 'quantity_change', 'current_quantity', 'notes']


@admin.register(StockAdjustment)
class StockAdjustmentAdmin(admin.ModelAdmin):
    """Admin configuration for StockAdjustment model."""
    list_display = ['id',
        'adjustment_number', 'warehouse', 'adjustment_date',
        'reason', 'status', 'organization', 'created_at'
    ]
    list_filter = ['status', 'reason', 'warehouse', 'organization', 'adjustment_date']
    search_fields = ['adjustment_number', 'notes']
    ordering = ['-adjustment_date']
    readonly_fields = ['approved_at', 'approved_by', 'created_at', 'updated_at']
    inlines = [StockAdjustmentItemInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'adjustment_number', 'adjustment_date', 'warehouse')
        }),
        ('Reason & Status', {
            'fields': ('reason', 'status', 'notes')
        }),
        ('Approval', {
            'fields': ('approved_at', 'approved_by'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
