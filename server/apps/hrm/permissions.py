"""
Custom DRF permission classes for HRM module.
"""
from rest_framework.permissions import BasePermission
from apps.core.utils.permission_helper import has_permission


class HasHRMPermission(BasePermission):
    """
    Custom permission class for HRM-specific permissions.
    
    This permission class integrates with the RBAC system to check if a user
    has the required HRM permission code through their assigned role.
    
    Super admins automatically bypass all permission checks.
    
    Usage in views/viewsets:
        permission_classes = [IsAuthenticated, HasHRMPermission]
        permission_code = 'hrm.employee.create'  # Set this in your view/viewset
    
    Or for dynamic permissions based on action:
        class EmployeeViewSet(viewsets.ModelViewSet):
            permission_classes = [IsAuthenticated, HasHRMPermission]
            
            def get_permissions(self):
                permission_map = {
                    'list': 'hrm.employee.read',
                    'retrieve': 'hrm.employee.read',
                    'create': 'hrm.employee.create',
                    'update': 'hrm.employee.update',
                    'partial_update': 'hrm.employee.update',
                    'destroy': 'hrm.employee.delete',
                }
                self.permission_code = permission_map.get(self.action)
                return super().get_permissions()
    """
    
    def __init__(self, permission_code=None):
        """
        Initialize with optional permission code.
        
        Args:
            permission_code: String permission code (e.g., 'hrm.employee.create')
        """
        self.permission_code = permission_code
        super().__init__()
    
    def has_permission(self, request, view):
        """
        Check if user has the required HRM permission.
        
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
