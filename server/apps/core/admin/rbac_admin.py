from django.contrib import admin
from apps.core.models import (
    Organization,
    Permission,
    Role,
    RolePermission,
)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """
    Admin configuration for Organization model.
    Displays organization details with filters for active status.
    """
    list_display = ('id','name', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    list_per_page = 25

    fieldsets = (
        ('Organization Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """
    Admin configuration for Permission model.
    Displays global permissions that can be assigned to roles.
    """
    list_display = ('id','name', 'permission_code', 'created_at')
    search_fields = ('name', 'permission_code', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('permission_code',)
    list_per_page = 25

    fieldsets = (
        ('Permission Information', {
            'fields': ('name', 'permission_code', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class RolePermissionInline(admin.TabularInline):
    """
    Inline admin for RolePermission to display permissions in Role admin.
    """
    model = RolePermission
    extra = 1
    fields = ('permission',)
    autocomplete_fields = ['permission']


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    Admin configuration for Role model.
    Displays organization-specific roles with their permissions.
    """
    list_display = ('id','name', 'organization', 'is_active', 'created_at')
    list_filter = ('organization', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('organization', 'name')
    list_per_page = 25
    inlines = [RolePermissionInline]

    fieldsets = (
        ('Role Information', {
            'fields': ('name', 'organization', 'description', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    """
    Admin configuration for RolePermission model.
    Manages the many-to-many relationship between roles and permissions.
    """
    list_display = ('id', 'role', 'permission', 'created_at')
    list_filter = ('role', 'permission')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('role', 'permission')
    list_per_page = 25

    fieldsets = (
        ('Role-Permission Assignment', {
            'fields': ('role', 'permission')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
