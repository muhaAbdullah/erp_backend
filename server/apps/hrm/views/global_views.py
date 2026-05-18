"""
ViewSets for HRM global master data tables (no organization).
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.hrm.models import Religion, Qualification
from apps.hrm.serializers import ReligionSerializer, QualificationSerializer
from apps.core.permissions import IsSuperAdmin
from apps.hrm.permissions import HasHRMPermission 
from apps.core.utils.audit_logger import log_action, get_model_changes
from drf_spectacular.utils import extend_schema, OpenApiResponse


class ReligionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing religions (global master data).
    
    Features:
    - Super admin only access
    - Global data (no organization)
    - Audit logging
    """
    queryset = Religion.objects.all()
    serializer_class = ReligionSerializer
    permission_classes = [IsAuthenticated, HasHRMPermission]
    permission_code = 'hrm.create_religions'
    filterset_fields = ['is_active']
    search_fields = ['name']
    ordering = ['name']
    
    @extend_schema(
        tags=['HRM - Global Master Data'],
        summary='List religions',
        description='Get list of religions (super admin only).',
        responses={200: ReligionSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        tags=['HRM - Global Master Data'],
        summary='Retrieve religion',
        responses={200: ReligionSerializer, 404: OpenApiResponse(description='Not found')}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        tags=['HRM - Global Master Data'],
        summary='Create religion',
        description='Create a new religion (super admin only).',
        request=ReligionSerializer,
        responses={201: ReligionSerializer, 400: OpenApiResponse(description='Validation error')}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Handle creation with audit logging."""
        instance = serializer.save()
        
        log_action(
            user=self.request.user,
            action='CREATE',
            model_name='Religion',
            object_id=instance.id,
            changes=get_model_changes(None, instance, ['name', 'description']),
            request=self.request
        )
    
    @extend_schema(
        tags=['HRM - Global Master Data'],
        summary='Update religion',
        request=ReligionSerializer,
        responses={200: ReligionSerializer, 400: OpenApiResponse(description='Validation error')}
    )
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_data = {'name': instance.name, 'description': instance.description}
        
        response = super().update(request, *args, **kwargs)
        updated_instance = self.get_object()
        
        log_action(
            user=request.user,
            action='UPDATE',
            model_name='Religion',
            object_id=updated_instance.id,
            changes={
                'before': old_data,
                'after': {'name': updated_instance.name, 'description': updated_instance.description}
            },
            request=request
        )
        return response
    
    @extend_schema(
        tags=['HRM - Global Master Data'],
        summary='Delete religion',
        responses={204: OpenApiResponse(description='Deleted')}
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance_id, instance_name = instance.id, instance.name
        
        response = super().destroy(request, *args, **kwargs)
        
        log_action(
            user=request.user,
            action='DELETE',
            model_name='Religion',
            object_id=instance_id,
            changes={'before': {'name': instance_name}, 'after': {}},
            request=request
        )
        return response


class QualificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing qualifications (global master data).
    
    Features:
    - Super admin only access
    - Global data (no organization)
    - Audit logging
    """
    queryset = Qualification.objects.all()
    serializer_class = QualificationSerializer
    permission_classes = [IsAuthenticated, HasHRMPermission]
    permission_code = 'hrm.create_qualifications'
    filterset_fields = ['is_active']
    search_fields = ['name', 'code', 'description']
    ordering = ['code', 'name']
    
    @extend_schema(
        tags=['HRM - Global Master Data'],
        summary='List qualifications',
        description='Get list of qualifications (super admin only).',
        responses={200: QualificationSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        tags=['HRM - Global Master Data'],
        summary='Retrieve qualification',
        responses={200: QualificationSerializer, 404: OpenApiResponse(description='Not found')}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        tags=['HRM - Global Master Data'],
        summary='Create qualification',
        description='Create a new qualification (super admin only).',
        request=QualificationSerializer,
        responses={201: QualificationSerializer, 400: OpenApiResponse(description='Validation error')}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Handle creation with audit logging."""
        instance = serializer.save()
        
        log_action(
            user=self.request.user,
            action='CREATE',
            model_name='Qualification',
            object_id=instance.id,
            changes=get_model_changes(None, instance, ['code', 'name', 'description']),
            request=self.request
        )
    
    @extend_schema(
        tags=['HRM - Global Master Data'],
        summary='Update qualification',
        request=QualificationSerializer,
        responses={200: QualificationSerializer, 400: OpenApiResponse(description='Validation error')}
    )
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_data = {'code': instance.code, 'name': instance.name}
        
        response = super().update(request, *args, **kwargs)
        updated_instance = self.get_object()
        
        log_action(
            user=request.user,
            action='UPDATE',
            model_name='Qualification',
            object_id=updated_instance.id,
            changes={
                'before': old_data,
                'after': {'code': updated_instance.code, 'name': updated_instance.name}
            },
            request=request
        )
        return response
    
    @extend_schema(
        tags=['HRM - Global Master Data'],
        summary='Delete qualification',
        responses={204: OpenApiResponse(description='Deleted')}
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance_id, instance_name = instance.id, instance.name
        
        response = super().destroy(request, *args, **kwargs)
        
        log_action(
            user=request.user,
            action='DELETE',
            model_name='Qualification',
            object_id=instance_id,
            changes={'before': {'name': instance_name}, 'after': {}},
            request=request
        )
        return response
