"""
ViewSet for Unit management.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.inventory.models import Unit
from apps.inventory.serializers import UnitSerializer, UnitListSerializer
from apps.inventory.permissions import HasInventoryPermission
from apps.core.utils.audit_logger import log_action, get_model_changes
from coresite.mixin.enforce_organization_mixin import EnforceOrganizationMixin
from drf_spectacular.utils import extend_schema
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class UnitViewSet(EnforceOrganizationMixin, viewsets.ModelViewSet):
    """ViewSet for unit of measurement management."""
    
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated, HasInventoryPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'code', 'symbol']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']
    
    def get_permissions(self):
        """Map actions to permission codes."""
        permission_map = {
            'list': 'inventory.view_units',
            'retrieve': 'inventory.view_units',
            'create': 'inventory.create_units',
            'update': 'inventory.update_units',
            'partial_update': 'inventory.update_units',
            'destroy': 'inventory.delete_units',
        }
        self.permission_code = permission_map.get(self.action, 'inventory.view_units')
        return super().get_permissions()
    
    def get_serializer_class(self):
        """Use lightweight serializer for list action."""
        if self.action == 'list':
            return UnitListSerializer
        return UnitSerializer
    
    def get_queryset(self):
        """Return filtered queryset based on user organization."""
        if getattr(self, 'swagger_fake_view', False):
            return Unit.objects.none()
        
        queryset = Unit.objects.select_related('organization')
        
        user = self.request.user
        if user.is_super_admin:
            return queryset
        elif user.organization:
            return queryset.filter(organization=user.organization)
        return Unit.objects.none()
    
    @extend_schema(tags=['Inventory - Units'], summary='List units')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(tags=['Inventory - Units'], summary='Retrieve unit details')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(tags=['Inventory - Units'], summary='Create unit')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Create unit with audit logging."""
        super().perform_create(serializer)
        unit = serializer.instance
        
        log_action(
            user=self.request.user,
            action='CREATE',
            model_name='Unit',
            object_id=unit.id,
            changes=get_model_changes(None, unit, ['code', 'name', 'symbol']),
            request=self.request
        )
    
    @extend_schema(tags=['Inventory - Units'], summary='Update unit')
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_data = {'code': instance.code, 'name': instance.name}
        
        response = super().update(request, *args, **kwargs)
        updated_instance = self.get_object()
        
        log_action(
            user=request.user,
            action='UPDATE',
            model_name='Unit',
            object_id=updated_instance.id,
            changes={'before': old_data, 'after': {'code': updated_instance.code, 'name': updated_instance.name}},
            request=request
        )
        
        return response
    
    @extend_schema(tags=['Inventory - Units'], summary='Delete unit')
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        log_action(
            user=request.user,
            action='DELETE',
            model_name='Unit',
            object_id=instance.id,
            changes={'code': instance.code, 'name': instance.name},
            request=request
        )
        
        return super().destroy(request, *args, **kwargs)
