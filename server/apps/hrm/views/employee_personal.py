"""
ViewSet for EmployeePersonal management.
"""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.hrm.models import EmployeePersonal
from apps.hrm.serializers import EmployeePersonalSerializer
from apps.hrm.permissions import HasHRMPermission
from apps.core.utils.audit_logger import log_action, get_model_changes
from drf_spectacular.utils import extend_schema, OpenApiResponse


class EmployeePersonalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing employee personal information.
    
    Features:
    - Permission-based access control
    - Cross-organization validation
    - Audit logging for all CRUD operations
    
    Required Permissions:
    - view_employee: View personal information
    - create_employee: Create personal information
    - update_employee: Update personal information
    - delete_employee: Delete personal information
    """
    queryset = EmployeePersonal.objects.all()
    serializer_class = EmployeePersonalSerializer
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
            return EmployeePersonal.objects.none()
        
        user = self.request.user
        if user.is_super_admin:
            return EmployeePersonal.objects.select_related(
                'employee', 'religion', 'qualification'
            ).all()
        elif user.organization:
            return EmployeePersonal.objects.select_related(
                'employee', 'religion', 'qualification'
            ).filter(employee__organization=user.organization)
        return EmployeePersonal.objects.none()
    
    @extend_schema(
        tags=['HRM - Employee Personal'],
        summary='List employee personal information',
        description='Get list of employee personal information records.',
        responses={200: EmployeePersonalSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        tags=['HRM - Employee Personal'],
        summary='Retrieve employee personal information',
        description='Get detailed personal information for a specific employee.',
        responses={
            200: EmployeePersonalSerializer,
            404: OpenApiResponse(description='Record not found'),
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        tags=['HRM - Employee Personal'],
        summary='Create employee personal information',
        description='Create personal information record for an employee.',
        request=EmployeePersonalSerializer,
        responses={
            201: EmployeePersonalSerializer,
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
            model_name='EmployeePersonal',
            object_id=record.id,
            changes=get_model_changes(None, record, [
                'employee', 'father_name', 'mother_name', 'marital_status'
            ]),
            request=self.request
        )
    
    @extend_schema(
        tags=['HRM - Employee Personal'],
        summary='Update employee personal information',
        description='Update personal information record.',
        request=EmployeePersonalSerializer,
        responses={
            200: EmployeePersonalSerializer,
            400: OpenApiResponse(description='Validation error'),
            404: OpenApiResponse(description='Record not found'),
        }
    )
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_data = {
            'father_name': instance.father_name,
            'mother_name': instance.mother_name,
            'marital_status': instance.marital_status,
        }
        
        response = super().update(request, *args, **kwargs)
        updated_instance = self.get_object()
        
        new_data = {
            'father_name': updated_instance.father_name,
            'mother_name': updated_instance.mother_name,
            'marital_status': updated_instance.marital_status,
        }
        
        log_action(
            user=request.user,
            action='UPDATE',
            model_name='EmployeePersonal',
            object_id=updated_instance.id,
            changes={'before': old_data, 'after': new_data},
            request=request
        )
        
        return response
    
    @extend_schema(
        tags=['HRM - Employee Personal'],
        summary='Partial update employee personal information',
        description='Partially update personal information record.',
        request=EmployeePersonalSerializer,
        responses={
            200: EmployeePersonalSerializer,
            400: OpenApiResponse(description='Validation error'),
            404: OpenApiResponse(description='Record not found'),
        }
    )
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_data = {
            'marital_status': instance.marital_status,
            'blood_group': instance.blood_group,
        }
        
        response = super().partial_update(request, *args, **kwargs)
        updated_instance = self.get_object()
        
        new_data = {
            'marital_status': updated_instance.marital_status,
            'blood_group': updated_instance.blood_group,
        }
        
        log_action(
            user=request.user,
            action='UPDATE',
            model_name='EmployeePersonal',
            object_id=updated_instance.id,
            changes={'before': old_data, 'after': new_data},
            request=request
        )
        
        return response
    
    @extend_schema(
        tags=['HRM - Employee Personal'],
        summary='Delete employee personal information',
        description='Delete personal information record.',
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
            model_name='EmployeePersonal',
            object_id=record_id,
            changes={
                'before': {'employee': employee_code},
                'after': {}
            },
            request=request
        )
        
        return response
