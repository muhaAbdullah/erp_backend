"""
ViewSet for Brand management.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.inventory.models import Brand
from apps.inventory.serializers import BrandSerializer, BrandListSerializer
from apps.inventory.permissions import HasInventoryPermission
from apps.core.utils.audit_logger import log_action, get_model_changes
from coresite.mixin.enforce_organization_mixin import EnforceOrganizationMixin
from drf_spectacular.utils import extend_schema
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class BrandViewSet(EnforceOrganizationMixin, viewsets.ModelViewSet):
    """ViewSet for brand management."""
    
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsAuthenticated, HasInventoryPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'country']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']
    
    def get_permissions(self):
        """Map actions to permission codes."""
        permission_map = {
            'list': 'inventory.view_brands',
            'retrieve': 'inventory.view_brands',
            'create': 'inventory.create_brands',
            'update': 'inventory.update_brands',
            'partial_update': 'inventory.update_brands',
            'destroy': 'inventory.delete_brands',
        }
        self.permission_code = permission_map.get(self.action, 'inventory.view_brands')
        return super().get_permissions()
    
    def get_serializer_class(self):
        """Use lightweight serializer for list action."""
        if self.action == 'list':
            return BrandListSerializer
        return BrandSerializer
    
    def get_queryset(self):
        """Return filtered queryset based on user organization."""
        if getattr(self, 'swagger_fake_view', False):
            return Brand.objects.none()
        
        queryset = Brand.objects.select_related('organization')
        
        user = self.request.user
        if user.is_super_admin:
            return queryset
        elif user.organization:
            return queryset.filter(organization=user.organization)
        return Brand.objects.none()
    
    @extend_schema(tags=['Inventory - Brands'], summary='List brands')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(tags=['Inventory - Brands'], summary='Retrieve brand details')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(tags=['Inventory - Brands'], summary='Create brand')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Create brand with audit logging."""
        super().perform_create(serializer)
        brand = serializer.instance
        
        log_action(
            user=self.request.user,
            action='CREATE',
            model_name='Brand',
            object_id=brand.id,
            changes=get_model_changes(None, brand, ['code', 'name', 'country']),
            request=self.request
        )
    
    @extend_schema(tags=['Inventory - Brands'], summary='Update brand')
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_data = {'code': instance.code, 'name': instance.name}
        
        response = super().update(request, *args, **kwargs)
        updated_instance = self.get_object()
        
        log_action(
            user=request.user,
            action='UPDATE',
            model_name='Brand',
            object_id=updated_instance.id,
            changes={'before': old_data, 'after': {'code': updated_instance.code, 'name': updated_instance.name}},
            request=request
        )
        
        return response
    
    @extend_schema(tags=['Inventory - Brands'], summary='Delete brand')
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        log_action(
            user=request.user,
            action='DELETE',
            model_name='Brand',
            object_id=instance.id,
            changes={'code': instance.code, 'name': instance.name},
            request=request
        )
        
        return super().destroy(request, *args, **kwargs)
