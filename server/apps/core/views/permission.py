"""
ViewSet for Permission management.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.core.models import Permission
from apps.core.serializers import PermissionSerializer, PermissionListSerializer
from apps.core.permissions import IsSuperAdmin
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


class PermissionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing permissions.
    Only super admins can create/update/delete permissions.
    All authenticated users can view permissions.
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'permission_code', 'description']
    ordering_fields = ['name', 'permission_code', 'created_at']
    ordering = ['permission_code']
    
    def get_serializer_class(self):
        """Use lightweight serializer for list action."""
        if self.action == 'list':
            return PermissionListSerializer
        return PermissionSerializer
    
    def get_permissions(self):
        """Super admin only for create, update, delete. Everyone can read."""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsSuperAdmin()]
        return [IsAuthenticated()]
    
    @extend_schema(
        tags=['Permissions'],
        summary='List all permissions',
        description='Get list of all available permissions in the system.',
        parameters=[
            OpenApiParameter('search', OpenApiTypes.STR, description='Search by name, code or description'),
        ],
        responses={
            200: PermissionListSerializer(many=True),
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        tags=['Permissions'],
        summary='Retrieve permission details',
        description='Get detailed information about a specific permission.',
        responses={
            200: PermissionSerializer,
            404: OpenApiResponse(description='Permission not found'),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        tags=['Permissions'],
        summary='Create new permission',
        description='Create a new permission. Only super admins can perform this action.',
        request=PermissionSerializer,
        responses={
            201: PermissionSerializer,
            400: OpenApiResponse(description='Validation error'),
            403: OpenApiResponse(description='Permission denied'),
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @extend_schema(
        tags=['Permissions'],
        summary='Update permission',
        description='Update an existing permission. Only super admins can perform this action.',
        request=PermissionSerializer,
        responses={
            200: PermissionSerializer,
            400: OpenApiResponse(description='Validation error'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Permission not found'),
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        tags=['Permissions'],
        summary='Partial update permission',
        description='Partially update a permission. Only super admins can perform this action.',
        request=PermissionSerializer,
        responses={
            200: PermissionSerializer,
            400: OpenApiResponse(description='Validation error'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Permission not found'),
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(
        tags=['Permissions'],
        summary='Delete permission',
        description='Delete a permission. Only super admins can perform this action.',
        responses={
            204: OpenApiResponse(description='Permission deleted successfully'),
            403: OpenApiResponse(description='Permission denied'),
            404: OpenApiResponse(description='Permission not found'),
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
