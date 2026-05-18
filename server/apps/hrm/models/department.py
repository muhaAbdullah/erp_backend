from django.db import models
from coresite.mixin.basemodel import BaseModel


class Department(BaseModel):
    """
    Department model with organization-level tenant isolation.
    
    Inherits from BaseModel to ensure multi-tenant isolation.
    Departments are organization-specific and used to group employees
    by their functional areas (e.g., HR, IT, Finance, Sales).
    
    Features:
    - Unique department codes per organization
    - Active/inactive status tracking
    - Automatic tenant filtering via TenantManager
    """
    
    name = models.CharField(
        max_length=100,
        help_text="Department name (e.g., Human Resources, Information Technology)"
    )
    code = models.CharField(
        max_length=20,
        help_text="Unique department code within organization (e.g., HR, IT, FIN)"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the department's purpose and responsibilities"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this department is currently active"
    )
    
    class Meta:
        unique_together = [['organization', 'code']]
        ordering = ['name']
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        indexes = [
            models.Index(fields=['organization', 'code']),
            models.Index(fields=['organization', 'is_active']),
        ]
    
    def __str__(self):
        """Return department code and name for admin readability."""
        return f"{self.code} - {self.name}"
