from django.db import models
from coresite.mixin import AbstractTimeStampModel


class RolePermission(AbstractTimeStampModel):
    """
    RolePermission model links roles to permissions.
    Many-to-many relationship between Role and Permission.
    """
    role = models.ForeignKey(
        'Role',
        on_delete=models.CASCADE,
        related_name='role_permissions',
        help_text="Role to assign permission to"
    )
    permission = models.ForeignKey(
        'Permission',
        on_delete=models.CASCADE,
        related_name='permission_roles',
        help_text="Permission to assign to role"
    )

    class Meta:
        verbose_name = 'Role Permission'
        verbose_name_plural = 'Role Permissions'
        unique_together = ('role', 'permission')
        ordering = ['role', 'permission']

    def __str__(self):
        return f"{self.role.name} - {self.permission.permission_code}"
