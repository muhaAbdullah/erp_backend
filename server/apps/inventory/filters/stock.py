"""
Filters for Stock models.
"""
import django_filters
from apps.inventory.models import (
    ProductStock, StockMovement, StockTransfer, StockAdjustment
)


class ProductStockFilter(django_filters.FilterSet):
    """
    Filter class for ProductStock model.
    
    Supports filtering by:
    - Product
    - Warehouse
    - Quantity range
    """
    
    product = django_filters.NumberFilter(field_name='product__id')
    warehouse = django_filters.NumberFilter(field_name='warehouse__id')
    
    # Quantity filters
    quantity_min = django_filters.NumberFilter(field_name='quantity', lookup_expr='gte')
    quantity_max = django_filters.NumberFilter(field_name='quantity', lookup_expr='lte')
    
    # Low stock filter (quantity less than product reorder level)
    low_stock = django_filters.BooleanFilter(method='filter_low_stock')
    
    # Ordering
    ordering = django_filters.OrderingFilter(
        fields=(
            ('product__name', 'product_name'),
            ('warehouse__name', 'warehouse_name'),
            ('quantity', 'quantity'),
            ('created_at', 'created_at'),
        )
    )
    
    def filter_low_stock(self, queryset, name, value):
        """Filter products with stock below reorder level."""
        from django.db.models import F
        
        if value:
            return queryset.filter(quantity__lt=F('product__reorder_level'))
        return queryset
    
    class Meta:
        model = ProductStock
        fields = ['product', 'warehouse']


class StockMovementFilter(django_filters.FilterSet):
    """
    Filter class for StockMovement model.
    
    Supports filtering by:
    - Product
    - Warehouse
    - Movement type
    - Date range
    """
    
    product = django_filters.NumberFilter(field_name='product__id')
    warehouse = django_filters.NumberFilter(field_name='warehouse__id')
    movement_type = django_filters.ChoiceFilter(choices=StockMovement.MOVEMENT_TYPE_CHOICES)
    
    # Date range filters
    date_from = django_filters.DateTimeFilter(field_name='movement_date', lookup_expr='gte')
    date_to = django_filters.DateTimeFilter(field_name='movement_date', lookup_expr='lte')
    
    # Reference filters
    reference_type = django_filters.CharFilter(lookup_expr='iexact')
    reference_number = django_filters.CharFilter(lookup_expr='icontains')
    
    # Ordering
    ordering = django_filters.OrderingFilter(
        fields=(
            ('movement_date', 'movement_date'),
            ('product__name', 'product_name'),
            ('warehouse__name', 'warehouse_name'),
            ('quantity', 'quantity'),
        )
    )
    
    class Meta:
        model = StockMovement
        fields = ['product', 'warehouse', 'movement_type', 'reference_type']


class StockTransferFilter(django_filters.FilterSet):
    """
    Filter class for StockTransfer model.
    
    Supports filtering by:
    - Transfer number
    - Source warehouse
    - Destination warehouse
    - Status
    - Date range
    """
    
    transfer_number = django_filters.CharFilter(lookup_expr='icontains')
    source_warehouse = django_filters.NumberFilter(field_name='source_warehouse__id')
    destination_warehouse = django_filters.NumberFilter(field_name='destination_warehouse__id')
    status = django_filters.ChoiceFilter(choices=StockTransfer.STATUS_CHOICES)
    
    # Date range filters
    date_from = django_filters.DateFilter(field_name='transfer_date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='transfer_date', lookup_expr='lte')
    
    # Ordering
    ordering = django_filters.OrderingFilter(
        fields=(
            ('transfer_date', 'transfer_date'),
            ('transfer_number', 'transfer_number'),
            ('created_at', 'created_at'),
        )
    )
    
    class Meta:
        model = StockTransfer
        fields = ['transfer_number', 'source_warehouse', 'destination_warehouse', 'status']


class StockAdjustmentFilter(django_filters.FilterSet):
    """
    Filter class for StockAdjustment model.
    
    Supports filtering by:
    - Adjustment number
    - Warehouse
    - Reason
    - Status
    - Date range
    """
    
    adjustment_number = django_filters.CharFilter(lookup_expr='icontains')
    warehouse = django_filters.NumberFilter(field_name='warehouse__id')
    reason = django_filters.ChoiceFilter(choices=StockAdjustment.REASON_CHOICES)
    status = django_filters.ChoiceFilter(choices=StockAdjustment.STATUS_CHOICES)
    
    # Date range filters
    date_from = django_filters.DateFilter(field_name='adjustment_date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='adjustment_date', lookup_expr='lte')
    
    # Ordering
    ordering = django_filters.OrderingFilter(
        fields=(
            ('adjustment_date', 'adjustment_date'),
            ('adjustment_number', 'adjustment_number'),
            ('created_at', 'created_at'),
        )
    )
    
    class Meta:
        model = StockAdjustment
        fields = ['adjustment_number', 'warehouse', 'reason', 'status']
