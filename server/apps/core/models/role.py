from django.db import models
from coresite.mixin import BaseModel


class Role(BaseModel):
    """
    Role model for RBAC with tenant isolation.
    
    Roles are organization-specific and define a set of permissions.
    Uses TenantManager for automatic filtering by organization.
    """
    name = models.CharField(max_length=255, help_text="Role name (e.g., 'Admin', 'Manager', 'User')")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    organization = models.ForeignKey('core.Organization', on_delete=models.CASCADE, related_name='roles')

    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        unique_together = ('name', 'organization')
        ordering = ['organization', 'name']

    def __str__(self):
        return f"{self.name} ({self.organization.name})"
