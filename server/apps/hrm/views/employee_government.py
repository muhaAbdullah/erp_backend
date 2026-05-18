"""
ViewSet for EmployeeGovernment management.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.hrm.models import EmployeeGovernment
from apps.hrm.serializers import EmployeeGovernmentSerializer
from apps.hrm.permissions import HasHRMPermission
from apps.core.utils.audit_logger import log_action, get_model_changes
from drf_spectacular.utils import extend_schema, OpenApiResponse


class EmployeeGovernmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing employee government information.
    
    Features:
    - Permission-based access control
    - Cross-organization validation
    - Audit logging for all CRUD operations
    
    Required Permissions:
    - view_employee: View government information
    - create_employee: Create government information
    - update_employee: Update government information
    - delete_employee: Delete government information
    """
    queryset = EmployeeGovernment.objects.all()
    serializer_class = EmployeeGovernmentSerializer
    permission_classes = [IsAuthenticated, HasHRMPermission]
    permission_code = 'view_employee'
    
    def get_permissions(self):
        """Set permission based on action."""
        permission_map = {
            'list': 'view_employee',
            'retrieve': 'view_employee',
            'create': 'create_employee',
            'update': 'update_employee',
            'partial_update': 'update_employee',
            'destroy': 'delete_employee',
        }
        self.permission_code = permission_map.get(self.action, 'view_employee')
        return super().get_permissions()
    
    def get_queryset(self):
        """Filter based on user's organization."""
        # Handle schema generation
        if getattr(self, 'swagger_fake_view', False):
            return EmployeeGovernment.objects.none()
        
        user = self.request.user
        if user.is_super_admin:
            return EmployeeGovernment.objects.select_related('employee').all()
        elif user.organization:
            return EmployeeGovernment.objects.select_related('employee').filter(
                employee__organization=user.organization
            )
        return EmployeeGovernment.objects.none()
    
    @extend_schema(
        tags=['HRM - Employee Government'],
        summary='List employee government information',
        description='Get list of employee government information records.',
        responses={200: EmployeeGovernmentSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        tags=['HRM - Employee Government'],
        summary='Retrieve employee government information',
        description='Get detailed government information for a specific employee.',
        responses={
            200: EmployeeGovernmentSerializer,
            404: OpenApiResponse(description='Record not found'),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        tags=['HRM - Employee Government'],
        summary='Create employee government information',
        description='Create government information record for an employee.',
        request=EmployeeGovernmentSerializer,
        responses={
            201: EmployeeGovernmentSerializer,
            400: OpenApiResponse(description='Validation error'),
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        """Handle creation with audit logging."""
        record = serializer.save()
        
        log_action(
            user=self.request.user,
            action='CREATE',
            model_name='EmployeeGovernment',
            object_id=record.id,
            changes=get_model_changes(None, record, [
                'employee', 'national_id', 'tax_identification', 'passport_number'
            ]),
            request=self.request
        )
    
    @extend_schema(
        tags=['HRM - Employee Government'],
        summary='Update employee government information',
        description='Update government information record.',
        request=EmployeeGovernmentSerializer,
        responses={
            200: EmployeeGovernmentSerializer,
            400: OpenApiResponse(description='Validation error'),
            404: OpenApiResponse(description='Record not found'),
        }
    )
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_data = {
            'national_id': instance.national_id,
            'tax_identification': instance.tax_identification,
            'passport_number': instance.passport_number,
        }
        
        response = super().update(request, *args, **kwargs)
        updated_instance = self.get_object()
        
        new_data = {
            'national_id': updated_instance.national_id,
            'tax_identification': updated_instance.tax_identification,
            'passport_number': updated_instance.passport_number,
        }
        
        log_action(
            user=request.user,
            action='UPDATE',
            model_name='EmployeeGovernment',
            object_id=updated_instance.id,
            changes={'before': old_data, 'after': new_data},
            request=request
        )
        
        return response
    
    @extend_schema(
        tags=['HRM - Employee Government'],
        summary='Partial update employee government information',
        description='Partially update government information record.',
        request=EmployeeGovernmentSerializer,
        responses={
            200: EmployeeGovernmentSerializer,
            400: OpenApiResponse(description='Validation error'),
            404: OpenApiResponse(description='Record not found'),
        }
    )
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_data = {
            'national_id': instance.national_id,
            'passport_number': instance.passport_number,
        }
        
        response = super().partial_update(request, *args, **kwargs)
        updated_instance = self.get_object()
        
        new_data = {
            'national_id': updated_instance.national_id,
            'passport_number': updated_instance.passport_number,
        }
        
        log_action(
            user=request.user,
            action='UPDATE',
            model_name='EmployeeGovernment',
            object_id=updated_instance.id,
            changes={'before': old_data, 'after': new_data},
            request=request
        )
        
        return response
    
    @extend_schema(
        tags=['HRM - Employee Government'],
        summary='Delete employee government information',
        description='Delete government information record.',
        responses={
            204: OpenApiResponse(description='Record deleted successfully'),
            404: OpenApiResponse(description='Record not found'),
        }
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        record_id = instance.id
        employee_code = instance.employee.employee_code
        
        response = super().destroy(request, *args, **kwargs)
        
        log_action(
            user=request.user,
            action='DELETE',
            model_name='EmployeeGovernment',
            object_id=record_id,
            changes={
                'before': {'employee': employee_code},
                'after': {}
            },
            request=request
        )
        
        return response
