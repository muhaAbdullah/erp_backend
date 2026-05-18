from django.db import models
from coresite.mixin.basemodel import BaseModel


class ScaleCategory(BaseModel):
    """
    Scale Category model with organization-level tenant isolation.
    
    Inherits from BaseModel to ensure multi-tenant isolation.
    Scale categories define salary grades or pay scales for employees
    (e.g., Scale A, Scale B, Executive Scale, Officer Scale).
    
    Features:
    - Unique scale category codes per organization
    - Active/inactive status tracking
    - Automatic tenant filtering via TenantManager
    """
    
    name = models.CharField(
        max_length=100,
        help_text="Scale category name (e.g., Scale A, Executive Scale, Officer Grade)"
    )
    code = models.CharField(
        max_length=20,
        help_text="Unique scale category code within organization (e.g., SA, SB, ES)"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the scale category and salary range"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this scale category is currently active"
    )
    
    class Meta:
        unique_together = [['organization', 'code']]
        ordering = ['name']
        verbose_name = 'Scale Category'
        verbose_name_plural = 'Scale Categories'
        indexes = [
            models.Index(fields=['organization', 'code']),
            models.Index(fields=['organization', 'is_active']),
        ]
    
    def __str__(self):
        """Return scale category code and name for admin readability."""
        return f"{self.code} - {self.name}"
