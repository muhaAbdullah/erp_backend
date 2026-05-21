"""
URL configuration for Inventory module.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.inventory.views import (
    CategoryViewSet,
    BrandViewSet,
    UnitViewSet,
    WarehouseViewSet,
    ProductViewSet,
    ProductStockViewSet,
    StockMovementViewSet,
    StockTransferViewSet,
    StockAdjustmentViewSet,
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'units', UnitViewSet, basename='unit')
router.register(r'warehouses', WarehouseViewSet, basename='warehouse')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'stocks', ProductStockViewSet, basename='productstock')
router.register(r'movements', StockMovementViewSet, basename='stockmovement')
router.register(r'transfers', StockTransferViewSet, basename='stocktransfer')
router.register(r'adjustments', StockAdjustmentViewSet, basename='stockadjustment')

urlpatterns = [
    path('', include(router.urls)),
]
