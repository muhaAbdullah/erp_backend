"""
Django admin interface for AuditLog model.
"""
from django.contrib import admin
from apps.core.models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Read-only admin interface for audit logs.
    """
    list_display = [
        'created_at',
        'user',
        'organization',
        'action',
        'model_name',
        'object_id',
        'ip_address'
    ]
    list_filter = ['action', 'model_name', 'created_at', 'organization']
    search_fields = ['user__email', 'user__username', 'model_name', 'object_id']
    readonly_fields = [
        'user', 'organization', 'action', 'model_name',
        'object_id', 'changes', 'ip_address', 'user_agent',
        'created_at', 'updated_at'
    ]
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        """Prevent manual addition of audit logs."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Prevent editing of audit logs."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Only super admins can delete logs (for cleanup)."""
        return request.user.is_superuser
