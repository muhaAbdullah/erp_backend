"""
ViewSet for EmployeeContact management.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.hrm.models import EmployeeContact
from apps.hrm.serializers import EmployeeContactSerializer
from apps.hrm.permissions import HasHRMPermission
from apps.core.utils.audit_logger import log_action, get_model_changes
from drf_spectacular.utils import extend_schema, OpenApiResponse


class EmployeeContactViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing employee contact information.
    
    Features:
    - Permission-based access control
    - Cross-organization validation
    - Audit logging for all CRUD operations
    
    Required Permissions:
    - view_employee: View contact information
    - create_employee: Create contact information
    - update_employee: Update contact information
    - delete_employee: Delete contact information
    """
    queryset = EmployeeContact.objects.all()
    serializer_class = EmployeeContactSerializer
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
            return EmployeeContact.objects.none()
        
        user = self.request.user
        if user.is_super_admin:
            return EmployeeContact.objects.select_related('employee').all()
        elif user.organization:
            return EmployeeContact.objects.select_related('employee').filter(
                employee__organization=user.organization
            )
        return EmployeeContact.objects.none()
    
    @extend_schema(
        tags=['HRM - Employee Contact'],
        summary='List employee contact information',
        description='Get list of employee contact information records.',
        responses={200: EmployeeContactSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        tags=['HRM - Employee Contact'],
        summary='Retrieve employee contact information',
        description='Get detailed contact information for a specific employee.',
        responses={
            200: EmployeeContactSerializer,
            404: OpenApiResponse(description='Record not found'),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        tags=['HRM - Employee Contact'],
        summary='Create employee contact information',
        description='Create contact information record for an employee.',
        request=EmployeeContactSerializer,
        responses={
            201: EmployeeContactSerializer,
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
            model_name='EmployeeContact',
            object_id=record.id,
            changes=get_model_changes(None, record, [
                'employee', 'mobile_number', 'personal_email', 'city'
            ]),
            request=self.request
        )
    
    @extend_schema(
        tags=['HRM - Employee Contact'],
        summary='Update employee contact information',
        description='Update contact information record.',
        request=EmployeeContactSerializer,
        responses={
            200: EmployeeContactSerializer,
            400: OpenApiResponse(description='Validation error'),
            404: OpenApiResponse(description='Record not found'),
        }
    )
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_data = {
            'mobile_number': instance.mobile_number,
            'personal_email': instance.personal_email,
            'city': instance.city,
        }
        
        response = super().update(request, *args, **kwargs)
        updated_instance = self.get_object()
        
        new_data = {
            'mobile_number': updated_instance.mobile_number,
            'personal_email': updated_instance.personal_email,
            'city': updated_instance.city,
        }
        
        log_action(
            user=request.user,
            action='UPDATE',
            model_name='EmployeeContact',
            object_id=updated_instance.id,
            changes={'before': old_data, 'after': new_data},
            request=request
        )
        
        return response
    
    @extend_schema(
        tags=['HRM - Employee Contact'],
        summary='Partial update employee contact information',
        description='Partially update contact information record.',
        request=EmployeeContactSerializer,
        responses={
            200: EmployeeContactSerializer,
            400: OpenApiResponse(description='Validation error'),
            404: OpenApiResponse(description='Record not found'),
        }
    )
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_data = {
            'mobile_number': instance.mobile_number,
            'personal_email': instance.personal_email,
        }
        
        response = super().partial_update(request, *args, **kwargs)
        updated_instance = self.get_object()
        
        new_data = {
            'mobile_number': updated_instance.mobile_number,
            'personal_email': updated_instance.personal_email,
        }
        
        log_action(
            user=request.user,
            action='UPDATE',
            model_name='EmployeeContact',
            object_id=updated_instance.id,
            changes={'before': old_data, 'after': new_data},
            request=request
        )
        
        return response
    
    @extend_schema(
        tags=['HRM - Employee Contact'],
        summary='Delete employee contact information',
        description='Delete contact information record.',
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
            model_name='EmployeeContact',
            object_id=record_id,
            changes={
                'before': {'employee': employee_code},
                'after': {}
            },
            request=request
        )
        
        return response
