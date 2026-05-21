"""
Custom DRF permission classes for Inventory module.
"""
from rest_framework.permissions import BasePermission
from apps.core.utils.permission_helper import has_permission


class HasInventoryPermission(BasePermission):
    """
    Custom permission class for Inventory-specific permissions.
    
    This permission class integrates with the RBAC system to check if a user
    has the required Inventory permission code through their assigned role.
    
    Super admins automatically bypass all permission checks.
    
    Usage in views/viewsets:
        permission_classes = [IsAuthenticated, HasInventoryPermission]
        permission_code = 'inventory.product.create'  # Set this in your view/viewset
    
    Or for dynamic permissions based on action:
        class ProductViewSet(viewsets.ModelViewSet):
            permission_classes = [IsAuthenticated, HasInventoryPermission]
            
            def get_permissions(self):
                permission_map = {
                    'list': 'inventory.product.read',
                    'retrieve': 'inventory.product.read',
                    'create': 'inventory.product.create',
                    'update': 'inventory.product.update',
                    'partial_update': 'inventory.product.update',
                    'destroy': 'inventory.product.delete',
                }
                self.permission_code = permission_map.get(self.action)
                return super().get_permissions()
    """
    
    def has_permission(self, request, view):
        """
        Check if user has the required Inventory permission.
        
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
        
        # Get permission code from view attribute
        # Note: ViewSet.get_permissions() sets self.permission_code on the VIEW instance
        permission_code = getattr(view, 'permission_code', None)
        
        # If no permission code is specified, deny access
        if not permission_code:
            return False
        
        # Check if user has the permission
        return has_permission(request.user, permission_code)
