"""
Optimized query selectors for Stock models.
"""
from django.db.models import Prefetch, Q
from apps.inventory.models import (
    ProductStock, StockMovement, StockTransfer, StockAdjustment
)


def stock_list_queryset(organization, warehouse_id=None):
    """
    Optimized queryset for stock listing.
    
    Args:
        organization: Organization instance
        warehouse_id: Optional warehouse ID to filter
    
    Returns:
        QuerySet: Optimized stock queryset
    """
    queryset = ProductStock.objects.filter(
        organization=organization
    ).select_related(
        'product',
        'product__category',
        'product__brand',
        'product__unit',
        'warehouse',
        'organization'
    )
    
    if warehouse_id:
        queryset = queryset.filter(warehouse_id=warehouse_id)
    
    return queryset.order_by('warehouse__name', 'product__name')


def stock_movement_list_queryset(organization, product_id=None, warehouse_id=None):
    """
    Optimized queryset for stock movement listing.
    
    Args:
        organization: Organization instance
        product_id: Optional product ID to filter
        warehouse_id: Optional warehouse ID to filter
    
    Returns:
        QuerySet: Optimized movement queryset
    """
    queryset = StockMovement.objects.filter(
        organization=organization
    ).select_related(
        'product',
        'product__unit',
        'warehouse',
        'organization'
    )
    
    if product_id:
        queryset = queryset.filter(product_id=product_id)
    
    if warehouse_id:
        queryset = queryset.filter(warehouse_id=warehouse_id)
    
    return queryset.order_by('-movement_date')


def stock_transfer_list_queryset(organization):
    """
    Optimized queryset for stock transfer listing.
    
    Args:
        organization: Organization instance
    
    Returns:
        QuerySet: Optimized transfer queryset
    """
    return StockTransfer.objects.filter(
        organization=organization
    ).select_related(
        'source_warehouse',
        'destination_warehouse',
        'completed_by',
        'organization'
    ).prefetch_related(
        Prefetch(
            'items',
            queryset=StockTransfer.items.through.objects.select_related(
                'product',
                'product__unit'
            )
        )
    ).order_by('-transfer_date')


def stock_transfer_detail_queryset(organization):
    """
    Optimized queryset for stock transfer detail view.
    
    Args:
        organization: Organization instance
    
    Returns:
        QuerySet: Optimized transfer queryset with all related data
    """
    return StockTransfer.objects.filter(
        organization=organization
    ).select_related(
        'source_warehouse',
        'destination_warehouse',
        'completed_by',
        'organization'
    ).prefetch_related(
        Prefetch(
            'items',
            queryset=StockTransfer.items.through.objects.select_related(
                'product',
                'product__category',
                'product__brand',
                'product__unit'
            ).order_by('id')
        )
    )


def stock_adjustment_list_queryset(organization):
    """
    Optimized queryset for stock adjustment listing.
    
    Args:
        organization: Organization instance
    
    Returns:
        QuerySet: Optimized adjustment queryset
    """
    return StockAdjustment.objects.filter(
        organization=organization
    ).select_related(
        'warehouse',
        'approved_by',
        'organization'
    ).prefetch_related(
        Prefetch(
            'items',
            queryset=StockAdjustment.items.through.objects.select_related(
                'product',
                'product__unit'
            )
        )
    ).order_by('-adjustment_date')


def stock_adjustment_detail_queryset(organization):
    """
    Optimized queryset for stock adjustment detail view.
    
    Args:
        organization: Organization instance
    
    Returns:
        QuerySet: Optimized adjustment queryset with all related data
    """
    return StockAdjustment.objects.filter(
        organization=organization
    ).select_related(
        'warehouse',
        'approved_by',
        'organization'
    ).prefetch_related(
        Prefetch(
            'items',
            queryset=StockAdjustment.items.through.objects.select_related(
                'product',
                'product__category',
                'product__brand',
                'product__unit'
            ).order_by('id')
        )
    )
