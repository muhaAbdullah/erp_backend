"""
Serializer for Employee model.
"""
from rest_framework import serializers
from apps.hrm.models import (
    Employee, Department, Designation, Shift,
    EmployeeType, ScaleCategory
)
from apps.core.serializers import OrganizationListSerializer
from .employee_personal import EmployeePersonalSerializer
from .employee_contact import EmployeeContactSerializer
from .employee_government import EmployeeGovernmentSerializer
from .department import DepartmentSerializer
from .designation import DesignationSerializer
from .shift import ShiftSerializer
from .employee_type import EmployeeTypeSerializer
from .scale_category import ScaleCategorySerializer


class EmployeeSerializer(serializers.ModelSerializer):
    """
    Serializer for Employee model with nested relationships.
    Organization is auto-assigned from request user, excluded from create/update.
    All ForeignKey relations must belong to the same organization.
    """
    organization = OrganizationListSerializer(read_only=True)
    organization_id = serializers.IntegerField(write_only=True, required=False)

    # Write: PrimaryKeyRelatedField
    department = serializers.PrimaryKeyRelatedField(
        queryset=Department.objects.none(),
        required=False,
        allow_null=True
    )
    designation = serializers.PrimaryKeyRelatedField(
        queryset=Designation.objects.none(),
        required=False,
        allow_null=True
    )
    shift = serializers.PrimaryKeyRelatedField(
        queryset=Shift.objects.none(),
        required=False,
        allow_null=True
    )
    employee_type = serializers.PrimaryKeyRelatedField(
        queryset=EmployeeType.objects.none(),
        required=False,
        allow_null=True
    )
    scale_category = serializers.PrimaryKeyRelatedField(
        queryset=ScaleCategory.objects.none(),
        required=False,
        allow_null=True
    )

    # Read: Nested serializers
    department_detail = DepartmentSerializer(source='department', read_only=True)
    designation_detail = DesignationSerializer(source='designation', read_only=True)
    shift_detail = ShiftSerializer(source='shift', read_only=True)
    employee_type_detail = EmployeeTypeSerializer(source='employee_type', read_only=True)
    scale_category_detail = ScaleCategorySerializer(source='scale_category', read_only=True)

    # Nested related data (read-only)
    personal_info = EmployeePersonalSerializer(read_only=True, allow_null=True)
    contact_info = EmployeeContactSerializer(read_only=True, allow_null=True)
    government_info = EmployeeGovernmentSerializer(read_only=True, allow_null=True)

    full_name = serializers.CharField(source='get_full_name', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_code', 'user',
            'department', 'department_detail',
            'designation', 'designation_detail',
            'shift', 'shift_detail',
            'employee_type', 'employee_type_detail',
            'scale_category', 'scale_category_detail',
            'first_name', 'middle_name', 'last_name', 'full_name',
            'date_of_birth', 'gender', 'joining_date',
            'employment_status', 'is_active',
            'personal_info', 'contact_info', 'government_info',
            'organization', 'organization_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'organization', 'full_name',
            'department_detail', 'designation_detail', 'shift_detail',
            'employee_type_detail', 'scale_category_detail',
            'personal_info', 'contact_info', 'government_info',
            'created_at', 'updated_at'
        ]

    def __init__(self, *args, **kwargs):
        """Set querysets based on request user's organization."""
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request, 'user') and hasattr(request.user, 'is_super_admin'):
            if request.user.is_super_admin:
                # Super admin can access all
                self.fields['department'].queryset = Department.objects.filter(is_active=True)
                self.fields['designation'].queryset = Designation.objects.filter(is_active=True)
                self.fields['shift'].queryset = Shift.objects.filter(is_active=True)
                self.fields['employee_type'].queryset = EmployeeType.objects.filter(is_active=True)
                self.fields['scale_category'].queryset = ScaleCategory.objects.filter(is_active=True)
            elif request.user.organization:
                # Regular users: filter by their organization
                org = request.user.organization
                self.fields['department'].queryset = Department.objects.filter(
                    organization=org, is_active=True
                )
                self.fields['designation'].queryset = Designation.objects.filter(
                    organization=org, is_active=True
                )
                self.fields['shift'].queryset = Shift.objects.filter(
                    organization=org, is_active=True
                )
                self.fields['employee_type'].queryset = EmployeeType.objects.filter(
                    organization=org, is_active=True
                )
                self.fields['scale_category'].queryset = ScaleCategory.objects.filter(
                    organization=org, is_active=True
                )
            else:
                # No organization: empty querysets
                self.fields['department'].queryset = Department.objects.none()
                self.fields['designation'].queryset = Designation.objects.none()
                self.fields['shift'].queryset = Shift.objects.none()
                self.fields['employee_type'].queryset = EmployeeType.objects.none()
                self.fields['scale_category'].queryset = ScaleCategory.objects.none()

    def validate(self, attrs):
        """Ensure all ForeignKey relations belong to the same organization."""
        request = self.context.get('request')
        if not request or not hasattr(request, 'user') or not hasattr(request.user, 'is_super_admin'):
            return attrs

        # Skip validation for super admin
        if request.user.is_super_admin:
            return attrs

        user_org = request.user.organization
        if not user_org:
            raise serializers.ValidationError("User must belong to an organization")

        # Validate all related objects belong to same organization
        related_fields = ['department', 'designation', 'shift', 'employee_type', 'scale_category']
        for field_name in related_fields:
            if field_name in attrs and attrs[field_name]:
                related_obj = attrs[field_name]
                if hasattr(related_obj, 'organization') and related_obj.organization != user_org:
                    raise serializers.ValidationError({
                        field_name: f"This {field_name} does not belong to your organization"
                    })

        return attrs

    def create(self, validated_data):
        """Remove organization_id from validated_data as it's handled by mixin."""
        validated_data.pop('organization_id', None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Remove organization_id from validated_data to prevent changes."""
        validated_data.pop('organization_id', None)
        return super().update(instance, validated_data)


class EmployeeListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for listing employees.
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    designation_name = serializers.CharField(source='designation.name', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_code', 'full_name',
            'department_name', 'designation_name',
            'employment_status', 'is_active'
        ]