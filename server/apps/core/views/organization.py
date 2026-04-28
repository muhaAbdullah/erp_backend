"""
ViewSet for Organization management.
"""
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.core.models import Organization
from apps.core.serializers import OrganizationSerializer, OrganizationListSerializer
from apps.core.permissions import IsSuperAdmin
from apps.core.utils.audit_logger import log_action, get_model_changes
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing organizations.
    Only super admins can create/update/delete organizations.
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        """Use lightweight serializer for list action."""
        if self.action == 'list':
            return OrganizationListSerializer
        return OrganizationSerializer
    
    def get_permissions(self):
        """Super admin only for create, update, delete."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSuperAdmin()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        """Filter organizations based on user role."""
        user = self.request.user
        if user.is_super_admin:
            return Organization.objects.all()
        elif user.organization:
            # Regular users can only see their own organization
            return Organization.objects.filter(id=user.organization.id)
        return Organization.objects.none()
    
    @extend_schema(
        tags=['Organizations'],
        summary='List all organizations',
        description='Get list of organizations. Super admins see all, regular users see only their organization.',
        parameters=[
            OpenApiParameter('is_active', OpenApiTypes.BOOL, description='Filter by active status'),
            OpenApiParameter('search', OpenApiTypes.STR, description='Search by name or description'),
        ],
        responses={
            200: OrganizationListSerializer(many=True),
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        tags=['Organizations'],
        summary='Retrieve organization details',
        description='Get detailed information about a specific organization.',
        responses={
            200: OrganizationSerializer,
            404: OpenApiResponse(description='Organization not found'),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        tags=['Organizations'],
        summary='Create new organization',
        description='Create a new organization. Only super admins can perform this action.',
        request=OrganizationSerializer,
        responses={
            201: OrganizationSerializer,
            400: OpenApiResponse(description='Validation error'),
            403: OpenApiResponse(description='Permission denied'),
        }
    )
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        
        # Log organization creation
        if response.status_code == status.HTTP_201_CREATED:
            org_id = response.data.get('id')
            organization = Organization.objects.get(id=org_id)
            
            log_action(
                user=request.user,
                action='CREATE',
                model_name='Organization',
                object_id=organization.id,
                changes=get_model_changes(None, organization, ['name', 'description']),
                request=request
            )
        
        return response
    
    @extend_schema(
        tags=['Organizations'],
        summary='Update organization',
        description='Update an existing organization. Only super admins can perform this action.',
        request=OrganizationSerializer,
        responses={
            200: OrganizationSerializer,
            400: OpenApiResponse(description='Validation error'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Organization not found'),
        }
    )
    def update(self, request, *args, **kwargs):
        # Get instance before update
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
            model_name='Organization',
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
        tags=['Organizations'],
        summary='Partial update organization',
        description='Partially update an organization. Only super admins can perform this action.',
        request=OrganizationSerializer,
        responses={
            200: OrganizationSerializer,
            400: OpenApiResponse(description='Validation error'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Organization not found'),
        }
    )
    def partial_update(self, request, *args, **kwargs):
        # Get instance before update
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
            model_name='Organization',
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
        tags=['Organizations'],
        summary='Delete organization',
        description='Delete an organization. Only super admins can perform this action.',
        responses={
            204: OpenApiResponse(description='Organization deleted successfully'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Organization not found'),
        }
    )
    def destroy(self, request, *args, **kwargs):
        # Get instance before deletion
        instance = self.get_object()
        org_id = instance.id
        org_name = instance.name
        
        response = super().destroy(request, *args, **kwargs)
        
        # Log the deletion
        log_action(
            user=request.user,
            action='DELETE',
            model_name='Organization',
            object_id=org_id,
            changes={'before': {'name': org_name}, 'after': {}},
            request=request
        )
        
        return response
    
    @extend_schema(
        tags=['Organizations'],
        summary='Get organization statistics',
        description='Get statistics for a specific organization (users count, roles count, etc.)',
        responses={
            200: OpenApiResponse(
                description='Organization statistics',
                response={
                    'type': 'object',
                    'properties': {
                        'users_count': {'type': 'integer'},
                        'roles_count': {'type': 'integer'},
                        'active_users_count': {'type': 'integer'},
                    }
                }
            ),
            404: OpenApiResponse(description='Organization not found'),
        }
    )
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get organization statistics."""
        organization = self.get_object()
        stats = {
            'users_count': organization.users.count(),
            'roles_count': organization.roles.count(),
            'active_users_count': organization.users.filter(is_active=True).count(),
        }
        return Response(stats)
