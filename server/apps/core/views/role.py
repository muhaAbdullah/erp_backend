"""
ViewSet for Role management with RBAC enforcement.
"""
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from apps.core.models import Role, RolePermission, Permission, Organization
from apps.core.serializers import (
    RoleSerializer,
    RoleListSerializer,
    AssignPermissionSerializer
)
from apps.core.permissions import HasPermission
from apps.core.utils.audit_logger import log_action, get_model_changes
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


class RoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing roles within an organization.
    
    Enforces:
    - Super admins must provide organization_id when creating roles
    - Org admins: Roles are automatically assigned to their organization
    - Permission-based access: Users need role.* permissions
    - Tenant filtering: Users only see roles from their organization
    
    Super admins can manage roles across all organizations.
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated, HasPermission]
    permission_code = 'role.read'  # Default permission
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_permissions(self):
        """Set permission based on action."""
        permission_map = {
            'list': 'role.read',
            'retrieve': 'role.read',
            'create': 'role.create',
            'update': 'role.update',
            'partial_update': 'role.update',
            'destroy': 'role.delete',
            'assign_permissions': 'role.update',
            'permissions': 'role.read',
        }
        self.permission_code = permission_map.get(self.action, 'role.read')
        return super().get_permissions()
    
    def get_serializer_class(self):
        """Use lightweight serializer for list action."""
        if self.action == 'list':
            return RoleListSerializer
        return RoleSerializer
    
    def get_queryset(self):
        """Filter roles based on user's organization."""
        user = self.request.user
        if user.is_super_admin:
            return Role.objects.all()
        elif user.organization:
            return Role.objects.filter(organization=user.organization)
        return Role.objects.none()
    
    @extend_schema(
        tags=['Roles'],
        summary='List all roles',
        description='Get list of roles in user\'s organization. Super admins see all roles.',
        parameters=[
            OpenApiParameter('is_active', OpenApiTypes.BOOL, description='Filter by active status'),
            OpenApiParameter('organization', OpenApiTypes.INT, description='Filter by organization ID'),
            OpenApiParameter('search', OpenApiTypes.STR, description='Search by name or description'),
        ],
        responses={
            200: RoleListSerializer(many=True),
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        tags=['Roles'],
        summary='Retrieve role details',
        description='Get detailed information about a specific role, including its permissions.',
        responses={
            200: RoleSerializer,
            404: OpenApiResponse(description='Role not found'),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        tags=['Roles'],
        summary='Create new role',
        description='Create a new role in user\'s organization. Only organization admins can perform this action.',
        request=RoleSerializer,
        responses={
            201: RoleSerializer,
            400: OpenApiResponse(description='Validation error'),
            403: OpenApiResponse(description='Permission denied'),
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """
        Handle organization assignment for role creation.
        
        - Super admin: Must provide organization_id in request
        - Org admin: Auto-assigned to their organization
        """
        if self.request.user.is_super_admin:
            # Super admin must provide organization_id
            organization_id = self.request.data.get('organization_id')
            if not organization_id:
                raise ValidationError({
                    "organization_id": "This field is required for super admin"
                })
            
            try:
                organization = Organization.objects.get(id=organization_id)
            except Organization.DoesNotExist:
                raise ValidationError({
                    "organization_id": "Organization not found"
                })
            
            role = serializer.save(organization=organization)
        else:
            # Org admin creates roles in their own organization
            if not self.request.user.organization:
                raise PermissionDenied("User must belong to an organization")
            
            role = serializer.save(organization=self.request.user.organization)
        
        # Log role creation
        log_action(
            user=self.request.user,
            action='CREATE',
            model_name='Role',
            object_id=role.id,
            changes=get_model_changes(None, role, ['name', 'description', 'organization']),
            request=self.request
        )
    
    @extend_schema(
        tags=['Roles'],
        summary='Update role',
        description='Update an existing role. Only organization admins can perform this action.',
        request=RoleSerializer,
        responses={
            200: RoleSerializer,
            400: OpenApiResponse(description='Validation error'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Role not found'),
        }
    )
    def update(self, request, *args, **kwargs):
        # Get the instance before update
        instance = self.get_object()
        old_name = instance.name
        old_description = instance.description
        old_is_active = instance.is_active
        
        response = super().update(request, *args, **kwargs)
        
        # Get updated instance
        updated_instance = self.get_object()
        
        # Log the update
        log_action(
            user=request.user,
            action='UPDATE',
            model_name='Role',
            object_id=updated_instance.id,
            changes={
                'before': {
                    'name': old_name,
                    'description': old_description,
                    'is_active': old_is_active
                },
                'after': {
                    'name': updated_instance.name,
                    'description': updated_instance.description,
                    'is_active': updated_instance.is_active
                }
            },
            request=request
        )
        
        return response
    
    @extend_schema(
        tags=['Roles'],
        summary='Partial update role',
        description='Partially update a role. Only organization admins can perform this action.',
        request=RoleSerializer,
        responses={
            200: RoleSerializer,
            400: OpenApiResponse(description='Validation error'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Role not found'),
        }
    )
    def partial_update(self, request, *args, **kwargs):
        # Get the instance before update
        instance = self.get_object()
        old_name = instance.name
        old_description = instance.description
        old_is_active = instance.is_active
        
        response = super().partial_update(request, *args, **kwargs)
        
        # Get updated instance
        updated_instance = self.get_object()
        
        # Log the update
        log_action(
            user=request.user,
            action='UPDATE',
            model_name='Role',
            object_id=updated_instance.id,
            changes={
                'before': {
                    'name': old_name,
                    'description': old_description,
                    'is_active': old_is_active
                },
                'after': {
                    'name': updated_instance.name,
                    'description': updated_instance.description,
                    'is_active': updated_instance.is_active
                }
            },
            request=request
        )
        
        return response
    
    @extend_schema(
        tags=['Roles'],
        summary='Delete role',
        description='Delete a role. Only organization admins can perform this action.',
        responses={
            204: OpenApiResponse(description='Role deleted successfully'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Role not found'),
        }
    )
    def destroy(self, request, *args, **kwargs):
        # Get instance before deletion
        instance = self.get_object()
        role_id = instance.id
        role_name = instance.name
        
        response = super().destroy(request, *args, **kwargs)
        
        # Log the deletion
        log_action(
            user=request.user,
            action='DELETE',
            model_name='Role',
            object_id=role_id,
            changes={'before': {'name': role_name}, 'after': {}},
            request=request
        )
        
        return response
    
    @extend_schema(
        tags=['Roles'],
        summary='Assign permissions to role',
        description='Assign multiple permissions to a role. Replaces existing permissions.',
        request=AssignPermissionSerializer,
        responses={
            200: OpenApiResponse(description='Permissions assigned successfully'),
            400: OpenApiResponse(description='Validation error'),
            404: OpenApiResponse(description='Role not found'),
        }
    )
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def assign_permissions(self, request, pk=None):
        """Assign permissions to a role."""
        role = self.get_object()
        serializer = AssignPermissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        permission_ids = serializer.validated_data['permission_ids']
        
        # Get old permissions before removal
        old_permissions = list(Permission.objects.filter(
            permission_roles__role=role
        ).values_list('permission_code', flat=True))
        
        # Remove existing permissions
        RolePermission.objects.filter(role=role).delete()
        
        # Add new permissions
        permissions = Permission.objects.filter(id__in=permission_ids)
        for permission in permissions:
            RolePermission.objects.create(role=role, permission=permission)
        
        # Get new permission codes
        new_permissions = [p.permission_code for p in permissions]
        
        # Log permission assignment
        log_action(
            user=request.user,
            action='ASSIGN_PERMISSION',
            model_name='Role',
            object_id=role.id,
            changes={
                'before': {'permissions': old_permissions},
                'after': {'permissions': new_permissions}
            },
            request=request
        )
        
        return Response({
            'message': f'Successfully assigned {len(permissions)} permissions to role {role.name}'
        })
    
    @extend_schema(
        tags=['Roles'],
        summary='Get role permissions',
        description='Get list of permissions assigned to this role.',
        responses={
            200: OpenApiResponse(
                description='List of permissions',
                response={
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'id': {'type': 'integer'},
                            'name': {'type': 'string'},
                            'permission_code': {'type': 'string'},
                        }
                    }
                }
            ),
            404: OpenApiResponse(description='Role not found'),
        }
    )
    @action(detail=True, methods=['get'])
    def permissions(self, request, pk=None):
        """Get permissions for a role."""
        role = self.get_object()
        permissions = Permission.objects.filter(
            permission_roles__role=role
        ).values('id', 'name', 'permission_code')
        return Response(permissions)
