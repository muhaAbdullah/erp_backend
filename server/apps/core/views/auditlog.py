"""
ViewSet for viewing audit logs (read-only).
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.core.models import AuditLog
from apps.core.serializers import AuditLogSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only ViewSet for viewing audit logs.
    Super admins see all logs.
    Regular users see only their organization's logs.
    """
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['action', 'model_name', 'user']
    search_fields = ['model_name', 'user__email', 'user__username']
    ordering_fields = ['created_at', 'action']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter logs by organization unless super admin."""
        if self.request.user.is_super_admin:
            return AuditLog.objects.all()
        
        # Regular users see only their organization's logs
        return AuditLog.objects.filter(organization=self.request.user.organization)
    
    @extend_schema(
        tags=['Audit Logs'],
        summary="List Audit Logs",
        description="View audit logs. Super admins see all logs, regular users see only their organization's logs.",
        parameters=[
            OpenApiParameter('action', OpenApiTypes.STR, description='Filter by action type'),
            OpenApiParameter('model_name', OpenApiTypes.STR, description='Filter by model name'),
            OpenApiParameter('user', OpenApiTypes.INT, description='Filter by user ID'),
            OpenApiParameter('search', OpenApiTypes.STR, description='Search by model name or user email/username'),
        ],
        responses={
            200: AuditLogSerializer(many=True),
            401: OpenApiResponse(description='Authentication required'),
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        tags=['Audit Logs'],
        summary="Retrieve Audit Log",
        description="Get details of a specific audit log entry.",
        responses={
            200: AuditLogSerializer,
            401: OpenApiResponse(description='Authentication required'),
            404: OpenApiResponse(description='Audit log not found'),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
