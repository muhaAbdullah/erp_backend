"""
Permission helper functions for RBAC system.
"""
from apps.core.models import RolePermission
from coresite.mixin.basemodel import set_current_user as _set_current_user, get_current_user as _get_current_user


def has_permission(user, permission_code):
    """
    Check if a user has a specific permission.
    """
    # Only super admins bypass all checks
    if user.is_super_admin:
        return True
    
    # Everyone else must have the permission via their role
    if not user.role:
        return False
    
    return RolePermission.objects.filter(
        role=user.role,
        permission__permission_code=permission_code
    ).exists()

def get_user_permissions(user):
    """
    Get all permission codes for a user.
    """
    # Only super admins get ALL permissions
    if user.is_super_admin:
        from apps.core.models import Permission
        return set(Permission.objects.values_list('permission_code', flat=True))
    
    # Everyone else (including org-admin/sub-admin) gets only their role's permissions
    if not user.role:
        return set()
    
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
