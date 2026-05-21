# Import services for easy access
from .stock import (
    complete_stock_transfer,
    approve_stock_adjustment,
    reject_stock_adjustment,
    add_opening_balance,
    record_purchase,
    record_sale,
    get_low_stock_products,
)
from .product import (
    get_product_stock_levels,
    get_products_by_category,
    calculate_inventory_value,
    get_stock_value_by_warehouse,
    get_product_movement_history,
    get_products_with_no_stock,
    get_products_summary,
)

__all__ = [
    'complete_stock_transfer',
    'approve_stock_adjustment',
    'reject_stock_adjustment',
    'add_opening_balance',
    'record_purchase',
    'record_sale',
    'get_low_stock_products',
    'get_product_stock_levels',
    'get_products_by_category',
    'calculate_inventory_value',
    'get_stock_value_by_warehouse',
    'get_product_movement_history',
    'get_products_with_no_stock',
    'get_products_summary',
]
