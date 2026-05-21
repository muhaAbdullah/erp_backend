"""
ViewSet for Warehouse management.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.inventory.models import Warehouse
from apps.inventory.serializers import WarehouseSerializer, WarehouseListSerializer
from apps.inventory.permissions import HasInventoryPermission
from apps.core.utils.audit_logger import log_action, get_model_changes
from coresite.mixin.enforce_organization_mixin import EnforceOrganizationMixin
from drf_spectacular.utils import extend_schema
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class WarehouseViewSet(EnforceOrganizationMixin, viewsets.ModelViewSet):
    """ViewSet for warehouse management."""
    
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    permission_classes = [IsAuthenticated, HasInventoryPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'city', 'state', 'country']
    search_fields = ['name', 'code', 'address', 'city']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']
    
    def get_permissions(self):
        """Map actions to permission codes."""
        permission_map = {
            'list': 'inventory.view_warehouses',
            'retrieve': 'inventory.view_warehouses',
            'create': 'inventory.create_warehouses',
            'update': 'inventory.update_warehouses',
            'partial_update': 'inventory.update_warehouses',
            'destroy': 'inventory.delete_warehouses',
        }
        self.permission_code = permission_map.get(self.action, 'inventory.view_warehouses')
        return super().get_permissions()
    
    def get_serializer_class(self):
        """Use lightweight serializer for list action."""
        if self.action == 'list':
            return WarehouseListSerializer
        return WarehouseSerializer
    
    def get_queryset(self):
        """Return filtered queryset based on user organization."""
        if getattr(self, 'swagger_fake_view', False):
            return Warehouse.objects.none()
        
        queryset = Warehouse.objects.select_related('organization')
        
        user = self.request.user
        if user.is_super_admin:
            return queryset
        elif user.organization:
            return queryset.filter(organization=user.organization)
        return Warehouse.objects.none()
    
    @extend_schema(tags=['Inventory - Warehouses'], summary='List warehouses')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(tags=['Inventory - Warehouses'], summary='Retrieve warehouse details')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(tags=['Inventory - Warehouses'], summary='Create warehouse')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Create warehouse with audit logging."""
        super().perform_create(serializer)
        warehouse = serializer.instance
        
        log_action(
            user=self.request.user,
            action='CREATE',
            model_name='Warehouse',
            object_id=warehouse.id,
            changes=get_model_changes(None, warehouse, ['code', 'name', 'city']),
            request=self.request
        )
    
    @extend_schema(tags=['Inventory - Warehouses'], summary='Update warehouse')
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_data = {'code': instance.code, 'name': instance.name}
        
        response = super().update(request, *args, **kwargs)
        updated_instance = self.get_object()
        
        log_action(
            user=request.user,
            action='UPDATE',
            model_name='Warehouse',
            object_id=updated_instance.id,
            changes={'before': old_data, 'after': {'code': updated_instance.code, 'name': updated_instance.name}},
            request=request
        )
        
        return response
    
    @extend_schema(tags=['Inventory - Warehouses'], summary='Delete warehouse')
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        log_action(
            user=request.user,
            action='DELETE',
            model_name='Warehouse',
            object_id=instance.id,
            changes={'code': instance.code, 'name': instance.name},
            request=request
        )
        
        return super().destroy(request, *args, **kwargs)
