"""
Product-related business logic services.
"""
from django.db.models import Sum, F, Q, DecimalField
from django.db.models.functions import Coalesce
from apps.inventory.models import Product, ProductStock


def get_product_stock_levels(product_id, organization):
    """
    Get stock levels for a product across all warehouses.
    
    Args:
        product_id: Product ID
        organization: Organization instance
    
    Returns:
        QuerySet: Stock records with warehouse details
    """
    stock_records = ProductStock.objects.filter(
        product_id=product_id,
        organization=organization
    ).select_related(
        'warehouse', 'product'
    ).order_by('warehouse__name')
    
    return stock_records


def get_products_by_category(category_id, organization, include_descendants=True):
    """
    Get all products in a category.
    
    Args:
        category_id: Category ID
        organization: Organization instance
        include_descendants: Include products from child categories
    
    Returns:
        QuerySet: Products in the category
    """
    from apps.inventory.models import Category
    
    category = Category.objects.get(pk=category_id, organization=organization)
    
    if include_descendants:
        # Get all descendant categories
        descendant_ids = [cat.id for cat in category.get_descendants()]
        category_ids = [category.id] + descendant_ids
        
        products = Product.objects.filter(
            organization=organization,
            category_id__in=category_ids
        )
    else:
        products = Product.objects.filter(
            organization=organization,
            category=category
        )
    
    return products.select_related('category', 'brand', 'unit')


def calculate_inventory_value(organization, warehouse_id=None):
    """
    Calculate total inventory value.
    
    Args:
        organization: Organization instance
        warehouse_id: Optional warehouse ID to filter by
    
    Returns:
        dict: Total value at cost and selling price
    """
    stock_qs = ProductStock.objects.filter(
        organization=organization
    ).select_related('product')
    
    if warehouse_id:
        stock_qs = stock_qs.filter(warehouse_id=warehouse_id)
    
    # Calculate totals
    total_cost_value = 0
    total_selling_value = 0
    
    for stock in stock_qs:
        total_cost_value += float(stock.quantity * stock.product.cost_price)
        total_selling_value += float(stock.quantity * stock.product.selling_price)
    
    return {
        'total_cost_value': round(total_cost_value, 2),
        'total_selling_value': round(total_selling_value, 2),
        'potential_profit': round(total_selling_value - total_cost_value, 2)
    }


def get_stock_value_by_warehouse(warehouse_id, organization):
    """
    Calculate inventory value for a specific warehouse.
    
    Args:
        warehouse_id: Warehouse ID
        organization: Organization instance
    
    Returns:
        dict: Warehouse stock value details
    """
    return calculate_inventory_value(organization, warehouse_id)


def get_product_movement_history(product_id, organization, warehouse_id=None, limit=50):
    """
    Get recent stock movements for a product.
    
    Args:
        product_id: Product ID
        organization: Organization instance
        warehouse_id: Optional warehouse ID to filter by
        limit: Maximum number of records to return
    
    Returns:
        QuerySet: Recent stock movements
    """
    from apps.inventory.models import StockMovement
    
    movements = StockMovement.objects.filter(
        product_id=product_id,
        organization=organization
    ).select_related('warehouse', 'product')
    
    if warehouse_id:
        movements = movements.filter(warehouse_id=warehouse_id)
    
    return movements.order_by('-movement_date')[:limit]


def get_products_with_no_stock(organization):
    """
    Get products with zero stock across all warehouses.
    
    Args:
        organization: Organization instance
    
    Returns:
        QuerySet: Products with no stock
    """
    products_with_stock = ProductStock.objects.filter(
        organization=organization,
        quantity__gt=0
    ).values_list('product_id', flat=True)
    
    products = Product.objects.filter(
        organization=organization,
        is_active=True
    ).exclude(
        id__in=products_with_stock
    ).select_related('category', 'brand', 'unit')
    
    return products


def get_products_summary(organization):
    """
    Get summary statistics for products.
    
    Args:
        organization: Organization instance
    
    Returns:
        dict: Summary statistics
    """
    from apps.inventory.models import Category, Brand
    
    total_products = Product.objects.filter(organization=organization).count()
    active_products = Product.objects.filter(organization=organization, is_active=True).count()
    total_categories = Category.objects.filter(organization=organization, is_active=True).count()
    total_brands = Brand.objects.filter(organization=organization, is_active=True).count()
    
    # Calculate total stock value
    inventory_value = calculate_inventory_value(organization)
    
    return {
        'total_products': total_products,
        'active_products': active_products,
        'inactive_products': total_products - active_products,
        'total_categories': total_categories,
        'total_brands': total_brands,
        'inventory_cost_value': inventory_value['total_cost_value'],
        'inventory_selling_value': inventory_value['total_selling_value'],
        'potential_profit': inventory_value['potential_profit']
    }
