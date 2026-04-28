"""
Audit logging helper service for tracking user actions.
"""
from django.db import models
from apps.core.models import AuditLog

def log_action(
    user,
    action,
    model_name,
    object_id=None,
    changes=None,
    request=None
):
    """
    Log an action to the audit log.
    
    Args:
        user: User who performed the action
        action: One of: CREATE, UPDATE, DELETE, LOGIN, LOGOUT, ASSIGN_PERMISSION, REMOVE_PERMISSION
        model_name: Name of the model (e.g., 'User', 'Role')
        object_id: ID of the affected object
        changes: Dict with 'before' and 'after' keys
        request: HTTP request object (optional, for IP address)
    """

    
    # Get IP address and user agent from request
    ip_address = None
    user_agent = None
    if request:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Get organization from user (for tenant filtering)
    organization = user.organization if user and hasattr(user, 'organization') else None
    
    # Create log entry
    AuditLog.objects.create(
        user=user,
        organization=organization,
        action=action,
        model_name=model_name,
        object_id=str(object_id) if object_id else None,
        changes=changes or {},
        ip_address=ip_address,
        user_agent=user_agent
    )


def get_client_ip(request):
    """
    Extract client IP address from request.
    Handles proxy headers (X-Forwarded-For).
    
    Args:
        request: HTTP request object
        
    Returns:
        str: Client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_model_changes(old_instance, new_instance, fields_to_track):
    """
    Compare two model instances and return changes.
    
    Args:
        old_instance: Original instance (or None for CREATE)
        new_instance: New instance
        fields_to_track: List of field names to track
    
    Returns:
        Dict with 'before' and 'after' keys containing field changes
    """
    changes = {
        'before': {},
        'after': {}
    }
    
    for field in fields_to_track:
        before_value = getattr(old_instance, field, None) if old_instance else None
        after_value = getattr(new_instance, field, None)
        
        # Convert model instances to readable strings
        if isinstance(before_value, models.Model):
            before_value = str(before_value)
        if isinstance(after_value, models.Model):
            after_value = str(after_value)
        
        # Handle None values
        if before_value is None:
            before_value = None
        if after_value is None:
            after_value = None
        
        changes['before'][field] = before_value
        changes['after'][field] = after_value
    
    return changes
