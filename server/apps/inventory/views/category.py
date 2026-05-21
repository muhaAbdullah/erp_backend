"""
ViewSet for Category management.
"""
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.inventory.models import Category
from apps.inventory.serializers import CategorySerializer, CategoryListSerializer
from apps.inventory.permissions import HasInventoryPermission
from apps.core.utils.audit_logger import log_action, get_model_changes
from coresite.mixin.enforce_organization_mixin import EnforceOrganizationMixin
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class CategoryViewSet(EnforceOrganizationMixin, viewsets.ModelViewSet):
    """ViewSet for product category management."""
    
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, HasInventoryPermission]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'parent']
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']
    
    def get_permissions(self):
        """Map actions to permission codes."""
        permission_map = {
            'list': 'inventory.view_categories',
            'retrieve': 'inventory.view_categories',
            'create': 'inventory.create_categories',
            'update': 'inventory.update_categories',
            'partial_update': 'inventory.update_categories',
            'destroy': 'inventory.delete_categories',
        }
        self.permission_code = permission_map.get(self.action, 'inventory.view_categories')
        return super().get_permissions()
    
    def get_serializer_class(self):
        """Use lightweight serializer for list action."""
        if self.action == 'list':
            return CategoryListSerializer
        return CategorySerializer
    
    def get_queryset(self):
        """Return filtered queryset based on user organization."""
        if getattr(self, 'swagger_fake_view', False):
            return Category.objects.none()
        
        queryset = Category.objects.select_related('parent', 'organization')
        
        user = self.request.user
        if user.is_super_admin:
            return queryset
        elif user.organization:
            return queryset.filter(organization=user.organization)
        return Category.objects.none()
    
    @extend_schema(tags=['Inventory - Categories'], summary='List categories')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(tags=['Inventory - Categories'], summary='Retrieve category details')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(tags=['Inventory - Categories'], summary='Create category')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Create category with audit logging."""
        super().perform_create(serializer)
        category = serializer.instance
        
        log_action(
            user=self.request.user,
            action='CREATE',
            model_name='Category',
            object_id=category.id,
            changes=get_model_changes(None, category, ['code', 'name', 'parent']),
            request=self.request
        )
    
    @extend_schema(tags=['Inventory - Categories'], summary='Update category')
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_data = {'code': instance.code, 'name': instance.name}
        
        response = super().update(request, *args, **kwargs)
        updated_instance = self.get_object()
        
        log_action(
            user=request.user,
            action='UPDATE',
            model_name='Category',
            object_id=updated_instance.id,
            changes={'before': old_data, 'after': {'code': updated_instance.code, 'name': updated_instance.name}},
            request=request
        )
        
        return response
    
    @extend_schema(tags=['Inventory - Categories'], summary='Delete category')
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        log_action(
            user=request.user,
            action='DELETE',
            model_name='Category',
            object_id=instance.id,
            changes={'code': instance.code, 'name': instance.name},
            request=request
        )
        
        return super().destroy(request, *args, **kwargs)
