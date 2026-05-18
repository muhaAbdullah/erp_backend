"""
Django admin configuration for Employee models.
"""
from django.contrib import admin
from apps.hrm.models import (
    Employee, EmployeePersonal, EmployeeContact, EmployeeGovernment
)


class EmployeePersonalInline(admin.StackedInline):
    """Inline admin for employee personal information."""
    model = EmployeePersonal
    extra = 0
    can_delete = False
    fields = [
        'father_name', 'mother_name', 'marital_status', 'blood_group',
        'nationality', 'religion', 'qualification',
        'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation'
    ]


class EmployeeContactInline(admin.StackedInline):
    """Inline admin for employee contact information."""
    model = EmployeeContact
    extra = 0
    can_delete = False
    fields = [
        'phone_primary', 'phone_secondary', 'email_personal', 'email_work',
        'address_line1', 'address_line2', 'city', 'state', 'country', 'postal_code'
    ]


class EmployeeGovernmentInline(admin.StackedInline):
    """Inline admin for employee government information."""
    model = EmployeeGovernment
    extra = 0
    can_delete = False
    fields = [
        'national_id', 'tax_id', 'social_security_number',
        'passport_number', 'passport_expiry',
        'driving_license_number', 'driving_license_expiry'
    ]


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Admin interface for Employee model."""
    list_display = [
        'employee_code', 'get_full_name', 'department', 'designation',
        'employment_status', 'is_active', 'organization'
    ]
    list_filter = [
        'organization', 'employment_status', 'is_active',
        'department', 'designation', 'gender'
    ]
    search_fields = [
        'employee_code', 'first_name', 'middle_name', 'last_name',
        'user__email'
    ]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'organization', 'employee_code', 'user',
                'first_name', 'middle_name', 'last_name',
                'date_of_birth', 'gender'
            )
        }),
        ('Employment Details', {
            'fields': (
                'department', 'designation', 'shift',
                'employee_type', 'scale_category',
                'joining_date', 'employment_status', 'is_active'
            )
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [EmployeePersonalInline, EmployeeContactInline, EmployeeGovernmentInline]
    
    def get_full_name(self, obj):
        """Display full name in list view."""
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'
    
    def get_queryset(self, request):
        """Filter by organization for non-super admin users."""
        qs = super().get_queryset(request)
        if request.user.is_super_admin:
            return qs
        elif request.user.organization:
            return qs.filter(organization=request.user.organization)
        return qs.none()
