from django.db import models
from coresite.mixin.basemodel import BaseModel


class Designation(BaseModel):
    """
    Designation model with organization-level tenant isolation.
    
    Inherits from BaseModel to ensure multi-tenant isolation.
    Designations represent job titles or positions within an organization
    (e.g., Manager, Senior Developer, Accountant).
    
    Features:
    - Unique designation codes per organization
    - Active/inactive status tracking
    - Automatic tenant filtering via TenantManager
    """
    
    name = models.CharField(
        max_length=100,
        help_text="Designation name (e.g., Senior Manager, Software Engineer)"
    )
    code = models.CharField(
        max_length=20,
        help_text="Unique designation code within organization (e.g., MGR, SE, ACC)"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the designation's role and responsibilities"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this designation is currently active"
    )
    
    class Meta:
        unique_together = [['organization', 'code']]
        ordering = ['name']
        verbose_name = 'Designation'
        verbose_name_plural = 'Designations'
        indexes = [
            models.Index(fields=['organization', 'code']),
            models.Index(fields=['organization', 'is_active']),
        ]
    
    def __str__(self):
        """Return designation code and name for admin readability."""
        return f"{self.code} - {self.name}"
