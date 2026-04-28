from django.db import models
from coresite.mixin import AbstractTimeStampModel
import threading


# Thread-local storage for current user context
_thread_locals = threading.local()


def set_current_user(user):
    """
    Set the current user in thread-local storage.
    This is used by TenantManager to filter querysets by organization.
    """
    _thread_locals.user = user


def get_current_user():
    """
    Get the current user from thread-local storage.
    Returns None if no user is set.
    """
    return getattr(_thread_locals, 'user', None)


class TenantManager(models.Manager):
    """
    Custom manager that automatically filters querysets by organization (tenant isolation).
    
    This manager ensures strict multi-tenancy by:
    - Filtering all queries to show only data from the user's organization
    - Allowing super admins to see all data across organizations
    - Preventing access to data when user has no organization
    
    Uses thread-local storage to get the current user's organization context,
    which is set by TenantMiddleware on each request.
    
    Usage:
        class MyModel(BaseModel):
            # BaseModel already includes TenantManager as default manager
            pass
        
        # In views, queries are automatically filtered:
        MyModel.objects.all()  # Only returns user's organization data
        
        # Super admin can explicitly access all data:
        MyModel.objects.all_tenants()  # Returns all data
    """

    def get_queryset(self):
        """
        Override get_queryset to filter by current user's organization.
        
        Filtering logic:
        - No authenticated user: Return unfiltered queryset (for public endpoints)
        - Super admin: Return all data (bypass tenant isolation)
        - Regular user with organization: Return only their organization's data
        - Regular user without organization: Return empty queryset
        
        Returns:
            QuerySet filtered by organization context
        """
        queryset = super().get_queryset()
        user = get_current_user()
        
        # No user context (e.g., unauthenticated requests, background tasks)
        if user is None or not user.is_authenticated:
            return queryset
        
        # Super admins bypass tenant filtering and see all data
        if getattr(user, 'is_super_admin', False):
            return queryset
        
        # Regular users see only their organization's data
        if hasattr(user, 'organization') and user.organization:
            return queryset.filter(organization=user.organization)
        
        # Users without organization see nothing (strict isolation)
        return queryset.none()

    def all_tenants(self):
        """
        Return queryset for all tenants without filtering.
        
        This bypasses tenant isolation and should only be used:
        - By super admins explicitly needing cross-tenant access
        - In background tasks that process all organizations
        - In admin interfaces with proper authorization
        
        Returns:
            Unfiltered QuerySet containing all organizations' data
        """
        return super().get_queryset()


class BaseModel(AbstractTimeStampModel):
    """
    Base model that includes organization field for multi-tenancy.
    All models that need tenant isolation should inherit from this.
    """
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        related_name='%(class)s_set',
        null=True,
        blank=True,
        help_text="Organization this record belongs to"
    )

    objects = TenantManager()

    class Meta:
        abstract = True
