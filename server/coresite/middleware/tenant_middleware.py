"""
Tenant middleware for multi-tenancy support.
Sets the current user in thread-local storage for each request.
"""
from apps.core.utils.permission_helper import set_current_user


class TenantMiddleware:
    """
    Middleware to set current user in thread-local storage.
    This enables tenant-aware querysets through TenantManager.
    """
    
    def __init__(self, get_response):
        """
        Initialize middleware.
        
        Args:
            get_response: Django get_response callable
        """
        self.get_response = get_response
    
    def __call__(self, request):
        """
        Process request and set current user.
        
        Args:
            request: Django HttpRequest object
        
        Returns:
            Django HttpResponse object
        """
        # Set current user from request
        if hasattr(request, 'user') and request.user.is_authenticated:
            set_current_user(request.user)
        else:
            set_current_user(None)
        
        # Process request
        response = self.get_response(request)
        
        # Clean up thread-local storage after request
        set_current_user(None)
        
        return response
