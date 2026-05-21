"""
ViewSet for Product management.
"""
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.inventory.models import Product
from apps.inventory.serializers import ProductSerializer, ProductListSerializer
from apps.inventory.filters import ProductFilter
from apps.inventory.permissions import HasInventoryPermission
from apps.inventory.services import get_product_stock_levels, get_low_stock_products
from apps.core.utils.audit_logger import log_action, get_model_changes
from coresite.mixin.enforce_organization_mixin import EnforceOrganizationMixin
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class ProductViewSet(EnforceOrganizationMixin, viewsets.ModelViewSet):
    """ViewSet for product management."""
    
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated, HasInventoryPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'code', 'barcode', 'description']
    ordering_fields = ['name', 'code', 'cost_price', 'selling_price', 'created_at']
    ordering = ['name']
    
    def get_permissions(self):
        """Map actions to permission codes."""
        permission_map = {
            'list': 'inventory.view_products',
            'retrieve': 'inventory.view_products',
            'create': 'inventory.create_products',
            'update': 'inventory.update_products',
            'partial_update': 'inventory.update_products',
            'destroy': 'inventory.delete_products',
            'stock_levels': 'inventory.view_products',
            'low_stock': 'inventory.view_products',
        }
        self.permission_code = permission_map.get(self.action, 'inventory.view_products')
        return super().get_permissions()
    
    def get_serializer_class(self):
        """Use lightweight serializer for list action."""
        if self.action == 'list':
            return ProductListSerializer
        return ProductSerializer
    
    def get_queryset(self):
        """Return filtered queryset based on user organization."""
        if getattr(self, 'swagger_fake_view', False):
            return Product.objects.none()
        
        queryset = Product.objects.select_related(
            'category', 'brand', 'unit', 'organization'
        ).prefetch_related('stock_records')
        
        user = self.request.user
        if user.is_super_admin:
            return queryset
        elif user.organization:
            return queryset.filter(organization=user.organization)
        return Product.objects.none()
    
    @extend_schema(tags=['Inventory - Products'], summary='List products')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(tags=['Inventory - Products'], summary='Retrieve product details')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(tags=['Inventory - Products'], summary='Create product')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Create product with audit logging."""
        super().perform_create(serializer)
        product = serializer.instance
        
        log_action(
            user=self.request.user,
            action='CREATE',
            model_name='Product',
            object_id=product.id,
            changes=get_model_changes(None, product, ['code', 'name', 'product_type']),
            request=self.request
        )
    
    @extend_schema(tags=['Inventory - Products'], summary='Update product')
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_data = {'code': instance.code, 'name': instance.name, 'cost_price': str(instance.cost_price)}
        
        response = super().update(request, *args, **kwargs)
        updated_instance = self.get_object()
        
        log_action(
            user=request.user,
            action='UPDATE',
            model_name='Product',
            object_id=updated_instance.id,
            changes={
                'before': old_data,
                'after': {
                    'code': updated_instance.code,
                    'name': updated_instance.name,
                    'cost_price': str(updated_instance.cost_price)
                }
            },
            request=request
        )
        
        return response
    
    @extend_schema(tags=['Inventory - Products'], summary='Delete product')
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        log_action(
            user=request.user,
            action='DELETE',
            model_name='Product',
            object_id=instance.id,
            changes={'code': instance.code, 'name': instance.name},
            request=request
        )
        
        return super().destroy(request, *args, **kwargs)
    
    @extend_schema(
        tags=['Inventory - Products'],
        summary='Get product stock levels across all warehouses'
    )
    @action(detail=True, methods=['get'], url_path='stock-levels')
    def stock_levels(self, request, pk=None):
        """Get stock levels for this product across all warehouses."""
        product = self.get_object()
        stock_records = get_product_stock_levels(product.id, request.user.organization)
        
        from apps.inventory.serializers import ProductStockListSerializer
        serializer = ProductStockListSerializer(stock_records, many=True)
        
        return Response(serializer.data)
    
    @extend_schema(
        tags=['Inventory - Products'],
        summary='Get products with low stock (below reorder level)'
    )
    @action(detail=False, methods=['get'], url_path='low-stock')
    def low_stock(self, request):
        """Get products with stock below reorder level."""
        products = get_low_stock_products(request.user.organization)
        
        serializer = ProductListSerializer(products, many=True)
        
        return Response(serializer.data)
