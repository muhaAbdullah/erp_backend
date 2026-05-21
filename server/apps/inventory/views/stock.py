"""
ViewSets for Stock management.
"""
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from apps.inventory.models import (
    ProductStock, StockMovement, StockTransfer, StockAdjustment
)
from apps.inventory.serializers import (
    ProductStockSerializer, ProductStockListSerializer,
    StockMovementSerializer, StockMovementListSerializer,
    StockTransferSerializer, StockTransferListSerializer,
    StockAdjustmentSerializer, StockAdjustmentListSerializer,
)
from apps.inventory.filters import (
    ProductStockFilter, StockMovementFilter,
    StockTransferFilter, StockAdjustmentFilter
)
from apps.inventory.permissions import HasInventoryPermission
from apps.inventory.services import (
    complete_stock_transfer, approve_stock_adjustment, reject_stock_adjustment
)
from apps.core.utils.audit_logger import log_action
from coresite.mixin.enforce_organization_mixin import EnforceOrganizationMixin
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class ProductStockViewSet(EnforceOrganizationMixin, viewsets.ModelViewSet):
    """ViewSet for product stock management."""
    
    queryset = ProductStock.objects.all()
    serializer_class = ProductStockSerializer
    permission_classes = [IsAuthenticated, HasInventoryPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductStockFilter
    search_fields = ['product__name', 'product__code', 'warehouse__name', 'warehouse__code']
    ordering_fields = ['quantity', 'product__name', 'warehouse__name', 'created_at']
    ordering = ['warehouse__name', 'product__name']
    
    def get_permissions(self):
        """Map actions to permission codes."""
        permission_map = {
            'list': 'inventory.view_stock',
            'retrieve': 'inventory.view_stock',
            'create': 'inventory.create_stock',
            'update': 'inventory.update_stock',
            'partial_update': 'inventory.update_stock',
            'destroy': 'inventory.delete_stock',
        }
        self.permission_code = permission_map.get(self.action, 'inventory.view_stock')
        return super().get_permissions()
    
    def get_serializer_class(self):
        """Use lightweight serializer for list action."""
        if self.action == 'list':
            return ProductStockListSerializer
        return ProductStockSerializer
    
    def get_queryset(self):
        """Return filtered queryset based on user organization."""
        if getattr(self, 'swagger_fake_view', False):
            return ProductStock.objects.none()
        
        queryset = ProductStock.objects.select_related(
            'product', 'product__category', 'product__brand', 'product__unit',
            'warehouse', 'organization'
        )
        
        user = self.request.user
        if user.is_super_admin:
            return queryset
        elif user.organization:
            return queryset.filter(organization=user.organization)
        return ProductStock.objects.none()
    
    @extend_schema(tags=['Inventory - Stock'], summary='List stock levels')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(tags=['Inventory - Stock'], summary='Retrieve stock details')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class StockMovementViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for stock movement history (read-only)."""
    
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer
    permission_classes = [IsAuthenticated, HasInventoryPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StockMovementFilter
    search_fields = ['product__name', 'product__code', 'reference_number']
    ordering_fields = ['movement_date', 'product__name', 'quantity']
    ordering = ['-movement_date']
    
    def get_permissions(self):
        """Map actions to permission codes."""
        permission_map = {
            'list': 'inventory.view_stock_movements',
            'retrieve': 'inventory.view_stock_movements',
        }
        self.permission_code = permission_map.get(self.action, 'inventory.view_stock_movements')
        return super().get_permissions()
    
    def get_serializer_class(self):
        """Use lightweight serializer for list action."""
        if self.action == 'list':
            return StockMovementListSerializer
        return StockMovementSerializer
    
    def get_queryset(self):
        """Return filtered queryset based on user organization."""
        if getattr(self, 'swagger_fake_view', False):
            return StockMovement.objects.none()
        
        queryset = StockMovement.objects.select_related(
            'product', 'product__unit', 'warehouse', 'organization'
        )
        
        user = self.request.user
        if user.is_super_admin:
            return queryset
        elif user.organization:
            return queryset.filter(organization=user.organization)
        return StockMovement.objects.none()
    
    @extend_schema(tags=['Inventory - Stock Movements'], summary='List stock movements')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(tags=['Inventory - Stock Movements'], summary='Retrieve movement details')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class StockTransferViewSet(EnforceOrganizationMixin, viewsets.ModelViewSet):
    """ViewSet for stock transfer management."""
    
    queryset = StockTransfer.objects.all()
    serializer_class = StockTransferSerializer
    permission_classes = [IsAuthenticated, HasInventoryPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StockTransferFilter
    search_fields = ['transfer_number', 'notes']
    ordering_fields = ['transfer_date', 'transfer_number', 'created_at']
    ordering = ['-transfer_date']
    
    def get_permissions(self):
        """Map actions to permission codes."""
        permission_map = {
            'list': 'inventory.view_transfers',
            'retrieve': 'inventory.view_transfers',
            'create': 'inventory.create_transfers',
            'update': 'inventory.update_transfers',
            'partial_update': 'inventory.update_transfers',
            'destroy': 'inventory.delete_transfers',
            'complete': 'inventory.complete_transfers',
            'cancel': 'inventory.complete_transfers',
        }
        self.permission_code = permission_map.get(self.action, 'inventory.view_transfers')
        return super().get_permissions()
    
    def get_serializer_class(self):
        """Use lightweight serializer for list action."""
        if self.action == 'list':
            return StockTransferListSerializer
        return StockTransferSerializer
    
    def get_queryset(self):
        """Return filtered queryset based on user organization."""
        if getattr(self, 'swagger_fake_view', False):
            return StockTransfer.objects.none()
        
        queryset = StockTransfer.objects.select_related(
            'source_warehouse', 'destination_warehouse',
            'completed_by', 'organization'
        ).prefetch_related('items__product')
        
        user = self.request.user
        if user.is_super_admin:
            return queryset
        elif user.organization:
            return queryset.filter(organization=user.organization)
        return StockTransfer.objects.none()
    
    @extend_schema(tags=['Inventory - Transfers'], summary='List stock transfers')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(tags=['Inventory - Transfers'], summary='Retrieve transfer details')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(tags=['Inventory - Transfers'], summary='Create stock transfer')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Create transfer with audit logging."""
        super().perform_create(serializer)
        transfer = serializer.instance
        
        log_action(
            user=self.request.user,
            action='CREATE',
            model_name='StockTransfer',
            object_id=transfer.id,
            changes={'transfer_number': transfer.transfer_number, 'status': transfer.status},
            request=self.request
        )
    
    @extend_schema(
        tags=['Inventory - Transfers'],
        summary='Complete/execute a pending stock transfer'
    )
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Execute a pending stock transfer."""
        try:
            transfer = complete_stock_transfer(pk, request.user, request)
            serializer = self.get_serializer(transfer)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        tags=['Inventory - Transfers'],
        summary='Cancel a stock transfer'
    )
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a stock transfer."""
        transfer = self.get_object()
        
        if transfer.status not in [StockTransfer.DRAFT, StockTransfer.PENDING]:
            return Response(
                {'error': 'Only DRAFT or PENDING transfers can be cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transfer.status = StockTransfer.CANCELLED
        transfer.save()
        
        log_action(
            user=request.user,
            action='CANCEL',
            model_name='StockTransfer',
            object_id=transfer.id,
            changes={'transfer_number': transfer.transfer_number, 'status': 'CANCELLED'},
            request=request
        )
        
        serializer = self.get_serializer(transfer)
        return Response(serializer.data)


class StockAdjustmentViewSet(EnforceOrganizationMixin, viewsets.ModelViewSet):
    """ViewSet for stock adjustment management."""
    
    queryset = StockAdjustment.objects.all()
    serializer_class = StockAdjustmentSerializer
    permission_classes = [IsAuthenticated, HasInventoryPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StockAdjustmentFilter
    search_fields = ['adjustment_number', 'notes']
    ordering_fields = ['adjustment_date', 'adjustment_number', 'created_at']
    ordering = ['-adjustment_date']
    
    def get_permissions(self):
        """Map actions to permission codes."""
        permission_map = {
            'list': 'inventory.view_adjustments',
            'retrieve': 'inventory.view_adjustments',
            'create': 'inventory.create_adjustments',
            'update': 'inventory.update_adjustments',
            'partial_update': 'inventory.update_adjustments',
            'destroy': 'inventory.delete_adjustments',
            'approve': 'inventory.approve_adjustments',
            'reject': 'inventory.approve_adjustments',
        }
        self.permission_code = permission_map.get(self.action, 'inventory.view_adjustments')
        return super().get_permissions()
    
    def get_serializer_class(self):
        """Use lightweight serializer for list action."""
        if self.action == 'list':
            return StockAdjustmentListSerializer
        return StockAdjustmentSerializer
    
    def get_queryset(self):
        """Return filtered queryset based on user organization."""
        if getattr(self, 'swagger_fake_view', False):
            return StockAdjustment.objects.none()
        
        queryset = StockAdjustment.objects.select_related(
            'warehouse', 'approved_by', 'organization'
        ).prefetch_related('items__product')
        
        user = self.request.user
        if user.is_super_admin:
            return queryset
        elif user.organization:
            return queryset.filter(organization=user.organization)
        return StockAdjustment.objects.none()
    
    @extend_schema(tags=['Inventory - Adjustments'], summary='List stock adjustments')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(tags=['Inventory - Adjustments'], summary='Retrieve adjustment details')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(tags=['Inventory - Adjustments'], summary='Create stock adjustment')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Create adjustment with audit logging."""
        super().perform_create(serializer)
        adjustment = serializer.instance
        
        log_action(
            user=self.request.user,
            action='CREATE',
            model_name='StockAdjustment',
            object_id=adjustment.id,
            changes={'adjustment_number': adjustment.adjustment_number, 'status': adjustment.status},
            request=self.request
        )
    
    @extend_schema(
        tags=['Inventory - Adjustments'],
        summary='Approve and execute a pending stock adjustment'
    )
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve and execute a pending stock adjustment."""
        try:
            adjustment = approve_stock_adjustment(pk, request.user, request)
            serializer = self.get_serializer(adjustment)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        tags=['Inventory - Adjustments'],
        summary='Reject a pending stock adjustment'
    )
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a pending stock adjustment."""
        try:
            reason = request.data.get('reason', None)
            adjustment = reject_stock_adjustment(pk, request.user, request, reason)
            serializer = self.get_serializer(adjustment)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
