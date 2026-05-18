"""
Django admin configuration for HRM master data models.
"""
from django.contrib import admin
from apps.hrm.models import (
    Department, Designation, Shift, EmployeeType, ScaleCategory
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Admin interface for Department model."""
    list_display = ['name', 'organization', 'is_active', 'created_at']
    list_filter = ['organization', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('organization', 'name', 'description', 'is_active')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Filter by organization for non-super admin users."""
        qs = super().get_queryset(request)
        if request.user.is_super_admin:
            return qs
        elif request.user.organization:
            return qs.filter(organization=request.user.organization)
        return qs.none()


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    """Admin interface for Designation model."""
    list_display = ['name', 'organization', 'is_active', 'created_at']
    list_filter = ['organization', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('organization', 'name', 'description', 'is_active')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Filter by organization for non-super admin users."""
        qs = super().get_queryset(request)
        if request.user.is_super_admin:
            return qs
        elif request.user.organization:
            return qs.filter(organization=request.user.organization)
        return qs.none()


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    """Admin interface for Shift model."""
    list_display = ['name', 'start_time', 'end_time', 'organization', 'is_active']
    list_filter = ['organization', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('organization', 'name', 'description', 'start_time', 'end_time', 'is_active')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Filter by organization for non-super admin users."""
        qs = super().get_queryset(request)
        if request.user.is_super_admin:
            return qs
        elif request.user.organization:
            return qs.filter(organization=request.user.organization)
        return qs.none()


@admin.register(EmployeeType)
class EmployeeTypeAdmin(admin.ModelAdmin):
    """Admin interface for EmployeeType model."""
    list_display = ['name', 'organization', 'is_active', 'created_at']
    list_filter = ['organization', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('organization', 'name', 'description', 'is_active')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Filter by organization for non-super admin users."""
        qs = super().get_queryset(request)
        if request.user.is_super_admin:
            return qs
        elif request.user.organization:
            return qs.filter(organization=request.user.organization)
        return qs.none()


@admin.register(ScaleCategory)
class ScaleCategoryAdmin(admin.ModelAdmin):
    """Admin interface for ScaleCategory model."""
    list_display = ['name', 'organization', 'is_active', 'created_at']
    list_filter = ['organization', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('organization', 'name', 'description', 'is_active')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Filter by organization for non-super admin users."""
        qs = super().get_queryset(request)
        if request.user.is_super_admin:
            return qs
        elif request.user.organization:
            return qs.filter(organization=request.user.organization)
        return qs.none()
