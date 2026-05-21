"""
Optimized query selectors for Product model.
"""
from django.db.models import Prefetch, Sum, Q
from apps.inventory.models import Product, ProductStock


def product_list_queryset(organization):
    """
    Optimized queryset for product listing.
    
    Args:
        organization: Organization instance
    
    Returns:
        QuerySet: Optimized product queryset
    """
    return Product.objects.filter(
        organization=organization
    ).select_related(
        'category',
        'brand',
        'unit',
        'organization'
    ).prefetch_related(
        Prefetch(
            'stock_records',
            queryset=ProductStock.objects.select_related('warehouse')
        )
    )


def product_detail_queryset(organization):
    """
    Optimized queryset for product detail view.
    
    Args:
        organization: Organization instance
    
    Returns:
        QuerySet: Optimized product queryset with all related data
    """
    return Product.objects.filter(
        organization=organization
    ).select_related(
        'category',
        'category__parent',
        'brand',
        'unit',
        'organization'
    ).prefetch_related(
        Prefetch(
            'stock_records',
            queryset=ProductStock.objects.select_related('warehouse').order_by('warehouse__name')
        ),
        Prefetch(
            'stock_movements',
            queryset=Product.stock_movements.through.objects.select_related(
                'warehouse'
            ).order_by('-movement_date')[:20]
        )
    )


def product_with_stock_queryset(organization, warehouse_id=None):
    """
    Get products with stock information.
    
    Args:
        organization: Organization instance
        warehouse_id: Optional warehouse ID to filter stock
    
    Returns:
        QuerySet: Products with annotated stock quantities
    """
    queryset = Product.objects.filter(
        organization=organization,
        is_active=True
    ).select_related(
        'category',
        'brand',
        'unit'
    )
    
    if warehouse_id:
        # Annotate with stock for specific warehouse
        queryset = queryset.annotate(
            stock_quantity=Sum(
                'stock_records__quantity',
                filter=Q(stock_records__warehouse_id=warehouse_id)
            )
        )
    else:
        # Annotate with total stock across all warehouses
        queryset = queryset.annotate(
            stock_quantity=Sum('stock_records__quantity')
        )
    
    return queryset


def low_stock_products_queryset(organization):
    """
    Get products below reorder level.
    
    Args:
        organization: Organization instance
    
    Returns:
        QuerySet: Products needing reorder
    """
    from django.db.models import F
    
    return Product.objects.filter(
        organization=organization,
        is_active=True
    ).annotate(
        total_stock=Sum('stock_records__quantity')
    ).filter(
        total_stock__lt=F('reorder_level')
    ).select_related(
        'category',
        'brand',
        'unit'
    ).order_by('total_stock')
