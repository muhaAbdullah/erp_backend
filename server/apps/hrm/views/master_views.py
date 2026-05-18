"""
ViewSets for HRM master data tables with organization enforcement.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.hrm.models import Department, Designation, Shift, EmployeeType, ScaleCategory
from apps.hrm.serializers import (
    DepartmentSerializer, DesignationSerializer, ShiftSerializer,
    EmployeeTypeSerializer, ScaleCategorySerializer
)
from apps.hrm.permissions import HasHRMPermission
from apps.core.utils.audit_logger import log_action, get_model_changes
from coresite.mixin.enforce_organization_mixin import EnforceOrganizationMixin
from drf_spectacular.utils import extend_schema, OpenApiResponse


class DepartmentViewSet(EnforceOrganizationMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing departments.
    
    Features:
    - Auto-assign organization from logged-in user
    - Permission-based access control (manage_hrm_masters or super admin)
    - Tenant filtering
    - Audit logging
    """
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, HasHRMPermission]
    permission_code = 'manage_hrm_masters'
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    def get_queryset(self):
        """Filter based on user's organization."""
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Department.objects.none()
        
        user = self.request.user
        if user.is_super_admin:
            return Department.objects.select_related('organization').all()
        elif user.organization:
            return Department.objects.filter(organization=user.organization)
        return Department.objects.none()
    
    @extend_schema(
        tags=['HRM - Master Data'],
        summary='List departments',
        description='Get list of departments in user\'s organization.',
        responses={200: DepartmentSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        tags=['HRM - Master Data'],
        summary='Retrieve department',
        responses={200: DepartmentSerializer, 404: OpenApiResponse(description='Not found')}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        tags=['HRM - Master Data'],
        summary='Create department',
        request=DepartmentSerializer,
        responses={201: DepartmentSerializer, 400: OpenApiResponse(description='Validation error')}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Handle creation with audit logging."""
        super().perform_create(serializer)
        instance = serializer.instance
        
        log_action(
            user=self.request.user,
            action='CREATE',
            model_name='Department',
            object_id=instance.id,
            changes=get_model_changes(None, instance, ['name', 'description']),
            request=self.request
        )
    
    @extend_schema(
        tags=['HRM - Master Data'],
        summary='Update department',
        request=DepartmentSerializer,
        responses={200: DepartmentSerializer, 400: OpenApiResponse(description='Validation error')}
    )
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_data = {'name': instance.name, 'description': instance.description}
        
        response = super().update(request, *args, **kwargs)
        updated_instance = self.get_object()
        
        log_action(
            user=request.user,
            action='UPDATE',
            model_name='Department',
            object_id=updated_instance.id,
            changes={
                'before': old_data,
                'after': {'name': updated_instance.name, 'description': updated_instance.description}
            },
            request=request
        )
        return response
    
    @extend_schema(
        tags=['HRM - Master Data'],
        summary='Delete department',
        responses={204: OpenApiResponse(description='Deleted')}
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance_id, instance_name = instance.id, instance.name
        
        response = super().destroy(request, *args, **kwargs)
        
        log_action(
            user=request.user,
            action='DELETE',
            model_name='Department',
            object_id=instance_id,
            changes={'before': {'name': instance_name}, 'after': {}},
            request=request
        )
        return response


class DesignationViewSet(EnforceOrganizationMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing designations.
    """
    queryset = Designation.objects.all()
    serializer_class = DesignationSerializer
    permission_classes = [IsAuthenticated, HasHRMPermission]
    permission_code = 'manage_hrm_masters'
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    def get_queryset(self):
        """Filter based on user's organization."""
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Designation.objects.none()
        
        user = self.request.user
        if user.is_super_admin:
            return Designation.objects.select_related('organization').all()
        elif user.organization:
            return Designation.objects.filter(organization=user.organization)
        return Designation.objects.none()
    
    @extend_schema(tags=['HRM - Master Data'], summary='List designations')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(tags=['HRM - Master Data'], summary='Retrieve designation')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(tags=['HRM - Master Data'], summary='Create designation')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        super().perform_create(serializer)
        instance = serializer.instance
        log_action(
            user=self.request.user, action='CREATE', model_name='Designation',
            object_id=instance.id, changes=get_model_changes(None, instance, ['name']),
            request=self.request
        )
    
    @extend_schema(tags=['HRM - Master Data'], summary='Update designation')
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_name = instance.name
        response = super().update(request, *args, **kwargs)
        updated_instance = self.get_object()
        log_action(
            user=request.user, action='UPDATE', model_name='Designation',
            object_id=updated_instance.id,
            changes={'before': {'name': old_name}, 'after': {'name': updated_instance.name}},
            request=request
        )
        return response
    
    @extend_schema(tags=['HRM - Master Data'], summary='Delete designation')
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance_id, instance_name = instance.id, instance.name
        response = super().destroy(request, *args, **kwargs)
        log_action(
            user=request.user, action='DELETE', model_name='Designation',
            object_id=instance_id, changes={'before': {'name': instance_name}, 'after': {}},
            request=request
        )
        return response


class ShiftViewSet(EnforceOrganizationMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing shifts.
    """
    queryset = Shift.objects.all()
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated, HasHRMPermission]
    permission_code = 'manage_hrm_masters'
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    def get_queryset(self):
        """Filter based on user's organization."""
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Shift.objects.none()
        
        user = self.request.user
        if user.is_super_admin:
            return Shift.objects.select_related('organization').all()
        elif user.organization:
            return Shift.objects.filter(organization=user.organization)
        return Shift.objects.none()
    
    @extend_schema(tags=['HRM - Master Data'], summary='List shifts')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(tags=['HRM - Master Data'], summary='Retrieve shift')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(tags=['HRM - Master Data'], summary='Create shift')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        instance = serializer.save(organization=self.request.user.organization)
        
        # Convert time objects to strings for JSON serialization
        changes = {
            'name': instance.name,
            'code': instance.code,
            'start_time': instance.start_time.strftime('%H:%M:%S') if instance.start_time else None,
            'end_time': instance.end_time.strftime('%H:%M:%S') if instance.end_time else None,
            'description': instance.description,
            'is_active': instance.is_active,
        }
        
        log_action(
            user=self.request.user,
            action='CREATE',
            model_name='Shift',
            object_id=instance.id,
            changes=changes,
            request=self.request
        )
    
    @extend_schema(tags=['HRM - Master Data'], summary='Update shift')
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_name = instance.name
        response = super().update(request, *args, **kwargs)
        updated_instance = self.get_object()
        log_action(
            user=request.user, action='UPDATE', model_name='Shift',
            object_id=updated_instance.id,
            changes={'before': {'name': old_name}, 'after': {'name': updated_instance.name}},
            request=request
        )
        return response
    
    @extend_schema(tags=['HRM - Master Data'], summary='Delete shift')
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance_id, instance_name = instance.id, instance.name
        response = super().destroy(request, *args, **kwargs)
        log_action(
            user=request.user, action='DELETE', model_name='Shift',
            object_id=instance_id, changes={'before': {'name': instance_name}, 'after': {}},
            request=request
        )
        return response


class EmployeeTypeViewSet(EnforceOrganizationMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing employee types.
    """
    queryset = EmployeeType.objects.all()
    serializer_class = EmployeeTypeSerializer
    permission_classes = [IsAuthenticated, HasHRMPermission]
    permission_code = 'manage_hrm_masters'
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    def get_queryset(self):
        """Filter based on user's organization."""
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return EmployeeType.objects.none()
        
        user = self.request.user
        if user.is_super_admin:
            return EmployeeType.objects.select_related('organization').all()
        elif user.organization:
            return EmployeeType.objects.filter(organization=user.organization)
        return EmployeeType.objects.none()
    
    @extend_schema(tags=['HRM - Master Data'], summary='List employee types')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(tags=['HRM - Master Data'], summary='Retrieve employee type')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(tags=['HRM - Master Data'], summary='Create employee type')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        super().perform_create(serializer)
        instance = serializer.instance
        log_action(
            user=self.request.user, action='CREATE', model_name='EmployeeType',
            object_id=instance.id, changes=get_model_changes(None, instance, ['name']),
            request=self.request
        )
    
    @extend_schema(tags=['HRM - Master Data'], summary='Update employee type')
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_name = instance.name
        response = super().update(request, *args, **kwargs)
        updated_instance = self.get_object()
        log_action(
            user=request.user, action='UPDATE', model_name='EmployeeType',
            object_id=updated_instance.id,
            changes={'before': {'name': old_name}, 'after': {'name': updated_instance.name}},
            request=request
        )
        return response
    
    @extend_schema(tags=['HRM - Master Data'], summary='Delete employee type')
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance_id, instance_name = instance.id, instance.name
        response = super().destroy(request, *args, **kwargs)
        log_action(
            user=request.user, action='DELETE', model_name='EmployeeType',
            object_id=instance_id, changes={'before': {'name': instance_name}, 'after': {}},
            request=request
        )
        return response


class ScaleCategoryViewSet(EnforceOrganizationMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing scale categories.
    """
    queryset = ScaleCategory.objects.all()
    serializer_class = ScaleCategorySerializer
    permission_classes = [IsAuthenticated, HasHRMPermission]
    permission_code = 'manage_hrm_masters'
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    def get_queryset(self):
        """Filter based on user's organization."""
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return ScaleCategory.objects.none()
        
        user = self.request.user
        if user.is_super_admin:
            return ScaleCategory.objects.select_related('organization').all()
        elif user.organization:
            return ScaleCategory.objects.filter(organization=user.organization)
        return ScaleCategory.objects.none()
    
    @extend_schema(tags=['HRM - Master Data'], summary='List scale categories')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(tags=['HRM - Master Data'], summary='Retrieve scale category')
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(tags=['HRM - Master Data'], summary='Create scale category')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        super().perform_create(serializer)
        instance = serializer.instance
        log_action(
            user=self.request.user, action='CREATE', model_name='ScaleCategory',
            object_id=instance.id, changes=get_model_changes(None, instance, ['name']),
            request=self.request
        )
    
    @extend_schema(tags=['HRM - Master Data'], summary='Update scale category')
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_name = instance.name
        response = super().update(request, *args, **kwargs)
        updated_instance = self.get_object()
        log_action(
            user=request.user, action='UPDATE', model_name='ScaleCategory',
            object_id=updated_instance.id,
            changes={'before': {'name': old_name}, 'after': {'name': updated_instance.name}},
            request=request
        )
        return response
    
    @extend_schema(tags=['HRM - Master Data'], summary='Delete scale category')
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance_id, instance_name = instance.id, instance.name
        response = super().destroy(request, *args, **kwargs)
        log_action(
            user=request.user, action='DELETE', model_name='ScaleCategory',
            object_id=instance_id, changes={'before': {'name': instance_name}, 'after': {}},
            request=request
        )
        return response
