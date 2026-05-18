from django.db import models
from coresite.mixin.basemodel import BaseModel


class EmployeeType(BaseModel):
    """
    Employee Type model with organization-level tenant isolation.
    
    Inherits from BaseModel to ensure multi-tenant isolation.
    Employee types classify employees by their employment nature
    (e.g., Permanent, Contract, Probation, Intern).
    
    Features:
    - Unique employee type codes per organization
    - Active/inactive status tracking
    - Automatic tenant filtering via TenantManager
    """
    
    name = models.CharField(
        max_length=100,
        help_text="Employee type name (e.g., Permanent, Contract, Probation, Intern)"
    )
    code = models.CharField(
        max_length=20,
        help_text="Unique employee type code within organization (e.g., PERM, CONT, PROB)"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the employee type and its terms"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this employee type is currently active"
    )
    
    class Meta:
        unique_together = [['organization', 'code']]
        ordering = ['name']
        verbose_name = 'Employee Type'
        verbose_name_plural = 'Employee Types'
        indexes = [
            models.Index(fields=['organization', 'code']),
            models.Index(fields=['organization', 'is_active']),
        ]
    
    def __str__(self):
        """Return employee type code and name for admin readability."""
        return f"{self.code} - {self.name}"
