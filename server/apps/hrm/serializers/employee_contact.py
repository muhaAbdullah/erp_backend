"""
Serializer for EmployeeContact model.
"""
from rest_framework import serializers
from apps.hrm.models import EmployeeContact, Employee


class EmployeeContactSerializer(serializers.ModelSerializer):
    """
    Serializer for EmployeeContact model.
    Links to employee with validation for same organization.
    """
    employee = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Employee.objects.none()
    )
    
    class Meta:
        model = EmployeeContact
        fields = [
            'id', 'employee', 'mobile_number', 'alternate_mobile',
            'personal_email', 'official_email',
            'present_address', 'permanent_address',
            'city', 'state', 'country', 'postal_code',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def __init__(self, *args, **kwargs):
        """Set employee queryset based on request user's organization."""
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request, 'user') and hasattr(request.user, 'is_super_admin'):
            if request.user.is_super_admin:
                self.fields['employee'].queryset = Employee.objects.all()
            elif request.user.organization:
                self.fields['employee'].queryset = Employee.objects.filter(
                    organization=request.user.organization
                )
            else:
                self.fields['employee'].queryset = Employee.objects.none()
    
    def validate_employee(self, value):
        """Ensure employee belongs to user's organization."""
        request = self.context.get('request')
        if request and hasattr(request, 'user') and hasattr(request.user, 'is_super_admin'):
            if not request.user.is_super_admin:
                if value.organization != request.user.organization:
                    raise serializers.ValidationError(
                        "Employee must belong to your organization"
                    )
        return value
