"""
Permission helper functions for RBAC system.
"""
from apps.core.models import RolePermission
from coresite.mixin.basemodel import set_current_user as _set_current_user, get_current_user as _get_current_user


def has_permission(user, permission_code):
    """
    Check if a user has a specific permission.
    
    Args:
        user: User instance
        permission_code: String permission code (e.g., 'user.create')
    
    Returns:
        Boolean indicating if user has the permission
    """
    # Super admins have all permissions
    if user.is_super_admin:
        return True
    
    # Admin users have all permissions
    if user.is_admin:
        return True
    
    # Check if user has a role
    if not user.role:
        return False
    
    # Check if user's role has the permission
    return RolePermission.objects.filter(
        role=user.role,
        permission__permission_code=permission_code
    ).exists()


def get_user_permissions(user):
    """
    Get all permission codes for a user.
    
    Args:
        user: User instance
    
    Returns:
        Set of permission codes (strings)
    """
    # Super admins and admins have all permissions
    if user.is_super_admin or user.is_admin:
        from apps.core.models import Permission
        return set(Permission.objects.values_list('permission_code', flat=True))
    
    # Check if user has a role
    if not user.role:
        return set()
    
    # Get all permissions for user's role
    return set(
        RolePermission.objects.filter(
            role=user.role
        ).values_list('permission__permission_code', flat=True)
    )


def set_current_user(user):
    """
    Set the current user in thread-local storage.
    This is used by TenantManager to filter querysets by organization.
    
    Args:
        user: User instance to set as current
    """
    _set_current_user(user)


def get_current_user():
    """
    Get the current user from thread-local storage.
    
    Returns:
        User instance or None if no user is set
    """
    return _get_current_user()
