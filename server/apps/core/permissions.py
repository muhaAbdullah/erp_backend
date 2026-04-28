"""
Custom DRF permission classes for RBAC.
"""
from rest_framework.permissions import BasePermission
from apps.core.utils.permission_helper import has_permission


class HasPermission(BasePermission):
    """
    Custom permission class that checks if user has specific permission code.
    
    This permission class integrates with the RBAC system to check if a user
    has the required permission code through their assigned role.
    
    Super admins automatically bypass all permission checks.
    
    Usage in views/viewsets:
        permission_classes = [IsAuthenticated, HasPermission]
        permission_code = 'user.create'  # Set this in your view/viewset
    
    Or for dynamic permissions based on action:
        class MyViewSet(viewsets.ModelViewSet):
            permission_classes = [IsAuthenticated, HasPermission]
            
            def get_permissions(self):
                permission_map = {
                    'list': 'user.read',
                    'retrieve': 'user.read',
                    'create': 'user.create',
                    'update': 'user.update',
                    'partial_update': 'user.update',
                    'destroy': 'user.delete',
                }
                self.permission_code = permission_map.get(self.action)
                return super().get_permissions()
    """
    
    def __init__(self, permission_code=None):
        """
        Initialize with optional permission code.
        
        Args:
            permission_code: String permission code (e.g., 'user.create')
        """
        self.permission_code = permission_code
        super().__init__()
    
    def has_permission(self, request, view):
        """
        Check if user has the required permission.
        
        Args:
            request: DRF Request object
            view: View object
        
        Returns:
            Boolean indicating if user has permission
        """
        # Must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Super admins bypass all checks
        if request.user.is_super_admin:
            return True
        
        # User must have a role assigned
        if not request.user.role:
            return False
        
        # Get permission code from instance or view
        permission_code = self.permission_code or getattr(view, 'permission_code', None)
        
        # If no permission code is specified, deny access
        if not permission_code:
            return False
        
        # Check if user has the permission
        return has_permission(request.user, permission_code)


class IsSuperAdmin(BasePermission):
    """
    Permission class that allows only super admins.
    """
    
    def has_permission(self, request, view):
        """Check if user is super admin."""
        return (
            request.user 
            and request.user.is_authenticated 
            and request.user.is_super_admin
        )


class IsOrganizationAdmin(BasePermission):
    """
    Permission class that allows only organization admins.
    Checks if user has admin role in their organization.
    """
    
    def has_permission(self, request, view):
        """Check if user is organization admin."""
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Super admins are always allowed
        if request.user.is_super_admin:
            return True
        
        # Check if user has admin role
        if request.user.role and request.user.role.name.lower() == 'admin':
            return True
        
        return False


class IsOwnerOrHasPermission(BasePermission):
    """
    Permission class that allows users to access their own resources
    without requiring specific permissions, but requires permissions
    for accessing other users' resources.
    
    This is useful for user profiles and similar resources where:
    - Users can always view/edit their own data
    - Viewing/editing other users' data requires specific permissions
    
    Usage:
        class UserProfileViewSet(viewsets.ModelViewSet):
            permission_classes = [IsAuthenticated, IsOwnerOrHasPermission]
            permission_code = 'user.read'  # For accessing other users
    """
    
    permission_code = None
    
    def __init__(self, permission_code=None):
        """
        Initialize with optional permission code.
        
        Args:
            permission_code: Permission code required for non-owner access
        """
        if permission_code:
            self.permission_code = permission_code
        super().__init__()
    
    def has_permission(self, request, view):
        """
        Check general access permission.
        Authenticated users can access their own data.
        """
        # Must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Super admins can access everything
        if request.user.is_super_admin:
            return True
        
        # All authenticated users can access (object-level permission handles the rest)
        return True
    
    def has_object_permission(self, request, view, obj):
        """
        Check object-level permission.
        
        Args:
            request: DRF Request object
            view: View object
            obj: Object being accessed
        
        Returns:
            Boolean indicating if user has permission
        """
        # Super admins can access everything
        if request.user.is_super_admin:
            return True
        
        # Allow users to access their own data
        # Check if obj is the user themselves
        if obj == request.user:
            return True
        
        # Check if obj has a 'user' attribute and it matches request.user
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        
        # For accessing other users' data, check permission
        permission_code = self.permission_code or getattr(view, 'permission_code', None)
        if not permission_code:
            # No permission code specified, deny access
            return False
        
        # User must have a role to check permissions
        if not request.user.role:
            return False
        
        # Check if user has the required permission
        return has_permission(request.user, permission_code)
