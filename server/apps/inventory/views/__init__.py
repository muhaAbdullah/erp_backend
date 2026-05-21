# Import all ViewSets for easy access
from .category import CategoryViewSet
from .brand import BrandViewSet
from .unit import UnitViewSet
from .warehouse import WarehouseViewSet
from .product import ProductViewSet
from .stock import (
    ProductStockViewSet,
    StockMovementViewSet,
    StockTransferViewSet,
    StockAdjustmentViewSet,
)

__all__ = [
    'CategoryViewSet',
    'BrandViewSet',
    'UnitViewSet',
    'WarehouseViewSet',
    'ProductViewSet',
    'ProductStockViewSet',
    'StockMovementViewSet',
    'StockTransferViewSet',
    'StockAdjustmentViewSet',
]
