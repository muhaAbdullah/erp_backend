# Import admin configurations to register them
from .inventory_admin import (
    CategoryAdmin,
    BrandAdmin,
    UnitAdmin,
    WarehouseAdmin,
    ProductAdmin,
    ProductStockAdmin,
    StockMovementAdmin,
    StockTransferAdmin,
    StockAdjustmentAdmin,
)

__all__ = [
    'CategoryAdmin',
    'BrandAdmin',
    'UnitAdmin',
    'WarehouseAdmin',
    'ProductAdmin',
    'ProductStockAdmin',
    'StockMovementAdmin',
    'StockTransferAdmin',
    'StockAdjustmentAdmin',
]
