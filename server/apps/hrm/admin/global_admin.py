"""
Django admin configuration for HRM global master data models.
"""
from django.contrib import admin
from apps.hrm.models import Religion, Qualification


@admin.register(Religion)
class ReligionAdmin(admin.ModelAdmin):
    """Admin interface for Religion model (global data)."""
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'is_active')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Qualification)
class QualificationAdmin(admin.ModelAdmin):
    """Admin interface for Qualification model (global data)."""
    list_display = ['code', 'name', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('code', 'name', 'description', 'is_active')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
