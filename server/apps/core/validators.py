"""
Security validators for RBAC and tenant isolation.
"""
from rest_framework.exceptions import ValidationError, PermissionDenied
from apps.core.utils.permission_helper import has_permission


def validate_organization_access(user, organization):
    """
    Ensure user can only access their own organization.
    
    Args:
        user: User instance
        organization: Organization instance to validate access to
    
    Returns:
        True if access is allowed
    
    Raises:
        PermissionDenied: If user cannot access the organization
    """
    if user.is_super_admin:
        return True
    
    if not user.organization:
        raise PermissionDenied("User has no organization assigned")
    
    if user.organization != organization:
        raise PermissionDenied("Cannot access other organizations")
    
    return True


def validate_role_organization(user, role):
    """
    Ensure role belongs to user's organization.
    
    Prevents assigning roles across organizations, maintaining tenant isolation.
    
    Args:
        user: User instance
        role: Role instance to validate
    
    Returns:
        True if validation passes
    
    Raises:
        ValidationError: If role doesn't belong to user's organization
    """
    if not role:
        # No role assigned is valid
        return True
    
    if user.is_super_admin:
        # Super admin can assign any role
        return True
    
    if not user.organization:
        raise ValidationError("User has no organization assigned")
    
    if role.organization != user.organization:
        raise ValidationError({
            "role": "Role must belong to user's organization"
        })
    
    return True


def validate_role_assignment(user, target_user, role):
    """
    Validate that a user can assign a role to a target user.
    
    Enforces:
    - Role must belong to target user's organization
    - Assigning user must have permission to assign roles
    
    Args:
        user: User performing the assignment
        target_user: User receiving the role
        role: Role being assigned
    
    Returns:
        True if validation passes
    
    Raises:
        ValidationError: If validation fails
        PermissionDenied: If user lacks permission
    """
    if not role:
        # Removing role is allowed
        return True
    
    # Must be same organization
    if role.organization != target_user.organization:
        raise ValidationError({
            "role": "Role must belong to target user's organization"
        })
    
    # User must have permission to assign roles (or be super admin)
    if not user.is_super_admin:
        # Check if user has role management permission
        if not has_permission(user, 'role.update') and not has_permission(user, 'user.update'):
            raise PermissionDenied("No permission to assign roles")
    
    return True


def validate_same_organization(user, target_object):
    """
    Generic validator to ensure an object belongs to user's organization.
    
    Args:
        user: User instance
        target_object: Object with organization field
    
    Returns:
        True if validation passes
    
    Raises:
        PermissionDenied: If object belongs to different organization
    """
    if user.is_super_admin:
        return True
    
    if not hasattr(target_object, 'organization'):
        # Object doesn't have organization field, skip validation
        return True
    
    if not user.organization:
        raise PermissionDenied("User has no organization assigned")
    
    if target_object.organization != user.organization:
        raise PermissionDenied("Cannot access objects from other organizations")
    
    return True
