"""
ViewSet for Employee management with multi-tenant RBAC enforcement.
"""
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from apps.hrm.models import Employee
from apps.hrm.serializers import EmployeeSerializer, EmployeeListSerializer
from apps.hrm.permissions import HasHRMPermission
from apps.core.utils.audit_logger import log_action, get_model_changes
from coresite.mixin.enforce_organization_mixin import EnforceOrganizationMixin
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend


class EmployeeViewSet(EnforceOrganizationMixin, viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, HasHRMPermission]
    permission_code = 'view_employee'
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['employment_status', 'is_active', 'department', 'designation']
    search_fields = ['employee_code', 'first_name', 'last_name', 'middle_name']
    ordering_fields = ['employee_code', 'joining_date', 'created_at']
    ordering = ['-created_at']

    def get_permissions(self):
        permission_map = {
            'list': 'view_employee',
            'retrieve': 'view_employee',
            'create': 'create_employee',
            'update': 'update_employee',
            'partial_update': 'update_employee',
            'destroy': 'delete_employee',
            'activate': 'update_employee',
            'deactivate': 'update_employee',
        }
        self.permission_code = permission_map.get(self.action, 'view_employee')
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        return EmployeeSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Employee.objects.none()

        queryset = Employee.objects.select_related(
            'organization', 'department', 'designation',
            'shift', 'employee_type', 'scale_category', 'user'
 ).select_related(
    'organization', 'department', 'designation',
    'shift', 'employee_type', 'scale_category', 'user',
    'personal_info', 'contact_info', 'government_info'
)

        user = self.request.user
        if user.is_super_admin:
            return queryset
        elif user.organization:
            return queryset.filter(organization=user.organization)
        return Employee.objects.none()

    @extend_schema(
        tags=['HRM - Employees'],
        summary='List all employees',
        parameters=[
            OpenApiParameter('employment_status', OpenApiTypes.STR),
            OpenApiParameter('is_active', OpenApiTypes.BOOL),
            OpenApiParameter('department', OpenApiTypes.INT),
            OpenApiParameter('designation', OpenApiTypes.INT),
            OpenApiParameter('search', OpenApiTypes.STR),
        ],
        responses={200: EmployeeListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(tags=['HRM - Employees'], summary='Retrieve employee details',
                   responses={200: EmployeeSerializer, 404: OpenApiResponse(description='Not found')})
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(tags=['HRM - Employees'], summary='Create new employee',
                   request=EmployeeSerializer,
                   responses={201: EmployeeSerializer, 400: OpenApiResponse(description='Validation error'),
                               403: OpenApiResponse(description='Permission denied')})
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """Handle employee creation with audit logging."""
        # Call super() so EnforceOrganizationMixin sets the organization
        super().perform_create(serializer)
        employee = serializer.instance

        log_action(
            user=self.request.user,
            action='CREATE',
            model_name='Employee',
            object_id=employee.id,
            changes=get_model_changes(None, employee, [
                'employee_code', 'first_name', 'last_name',
                'department', 'designation', 'employment_status'
            ]),
            request=self.request
        )

    @extend_schema(tags=['HRM - Employees'], summary='Update employee',
                   request=EmployeeSerializer,
                   responses={200: EmployeeSerializer, 400: OpenApiResponse(description='Validation error'),
                               403: OpenApiResponse(description='Permission denied'),
                               404: OpenApiResponse(description='Not found')})
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_data = {
            'employee_code': instance.employee_code,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'department': str(instance.department) if instance.department else None,
            'designation': str(instance.designation) if instance.designation else None,
            'employment_status': instance.employment_status,
        }

        response = super().update(request, *args, **kwargs)
        updated_instance = self.get_object()

        log_action(
            user=request.user,
            action='UPDATE',
            model_name='Employee',
            object_id=updated_instance.id,
            changes={
                'before': old_data,
                'after': {
                    'employee_code': updated_instance.employee_code,
                    'first_name': updated_instance.first_name,
                    'last_name': updated_instance.last_name,
                    'department': str(updated_instance.department) if updated_instance.department else None,
                    'designation': str(updated_instance.designation) if updated_instance.designation else None,
                    'employment_status': updated_instance.employment_status,
                }
            },
            request=request
        )
        return response

    @extend_schema(tags=['HRM - Employees'], summary='Partial update employee',
                   request=EmployeeSerializer,
                   responses={200: EmployeeSerializer, 400: OpenApiResponse(description='Validation error'),
                               403: OpenApiResponse(description='Permission denied'),
                               404: OpenApiResponse(description='Not found')})
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        old_data = {
            'employee_code': instance.employee_code,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'employment_status': instance.employment_status,
            'is_active': instance.is_active,
        }

        response = super().partial_update(request, *args, **kwargs)
        updated_instance = self.get_object()

        log_action(
            user=request.user,
            action='UPDATE',
            model_name='Employee',
            object_id=updated_instance.id,
            changes={
                'before': old_data,
                'after': {
                    'employee_code': updated_instance.employee_code,
                    'first_name': updated_instance.first_name,
                    'last_name': updated_instance.last_name,
                    'employment_status': updated_instance.employment_status,
                    'is_active': updated_instance.is_active,
                }
            },
            request=request
        )
        return response

    @extend_schema(tags=['HRM - Employees'], summary='Delete employee',
                   responses={204: OpenApiResponse(description='Deleted'),
                               403: OpenApiResponse(description='Permission denied'),
                               404: OpenApiResponse(description='Not found')})
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        employee_id = instance.id
        employee_code = instance.employee_code
        employee_name = instance.get_full_name()

        response = super().destroy(request, *args, **kwargs)

        log_action(
            user=request.user,
            action='DELETE',
            model_name='Employee',
            object_id=employee_id,
            changes={'before': {'employee_code': employee_code, 'name': employee_name}, 'after': {}},
            request=request
        )
        return response

    @extend_schema(tags=['HRM - Employees'], summary='Activate employee',
                   responses={200: OpenApiResponse(description='Activated'),
                               404: OpenApiResponse(description='Not found')})
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        employee = self.get_object()
        if employee.is_active:
            return Response({'message': 'Employee is already active'}, status=status.HTTP_400_BAD_REQUEST)
        employee.is_active = True
        employee.save()
        log_action(user=request.user, action='UPDATE', model_name='Employee',
                   object_id=employee.id,
                   changes={'before': {'is_active': False}, 'after': {'is_active': True}},
                   request=request)
        return Response({'message': f'Employee {employee.employee_code} activated successfully'})

    @extend_schema(tags=['HRM - Employees'], summary='Deactivate employee',
                   responses={200: OpenApiResponse(description='Deactivated'),
                               404: OpenApiResponse(description='Not found')})
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        employee = self.get_object()
        if not employee.is_active:
            return Response({'message': 'Employee is already inactive'}, status=status.HTTP_400_BAD_REQUEST)
        employee.is_active = False
        employee.save()
        log_action(user=request.user, action='UPDATE', model_name='Employee',
                   object_id=employee.id,
                   changes={'before': {'is_active': True}, 'after': {'is_active': False}},
                   request=request)
        return Response({'message': f'Employee {employee.employee_code} deactivated successfully'})