from django.db import models
from coresite.mixin import AbstractTimeStampModel


class Permission(AbstractTimeStampModel):
    """
    Permission model for RBAC.
    Defines global permissions that can be assigned to roles.
    """
    name = models.CharField(max_length=255, help_text="Human-readable permission name (e.g., 'Create User')")
    permission_code = models.CharField(
        max_length=255, 
        unique=True, 
        db_index=True,
        help_text="Unique code for permission (e.g., 'user.create')"
    )
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'
        ordering = ['permission_code']

    def __str__(self):
        return f"{self.name} ({self.permission_code})"
