from django.db import models
from coresite.mixin.basemodel import BaseModel


class Shift(BaseModel):
    """
    Shift model with organization-level tenant isolation.
    
    Inherits from BaseModel to ensure multi-tenant isolation.
    Shifts define working hours for employees within an organization
    (e.g., Morning Shift, Night Shift, General Shift).
    
    Features:
    - Unique shift codes per organization
    - Start and end time tracking
    - Active/inactive status tracking
    - Automatic tenant filtering via TenantManager
    """
    
    name = models.CharField(
        max_length=100,
        help_text="Shift name (e.g., Morning Shift, Night Shift, General)"
    )
    code = models.CharField(
        max_length=20,
        help_text="Unique shift code within organization (e.g., MS, NS, GS)"
    )
    start_time = models.TimeField(
        help_text="Shift start time (e.g., 08:00:00)"
    )
    end_time = models.TimeField(
        help_text="Shift end time (e.g., 17:00:00)"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the shift timing and requirements"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this shift is currently active"
    )
    
    class Meta:
        unique_together = [['organization', 'code']]
        ordering = ['name']
        verbose_name = 'Shift'
        verbose_name_plural = 'Shifts'
        indexes = [
            models.Index(fields=['organization', 'code']),
            models.Index(fields=['organization', 'is_active']),
        ]
    
    def __str__(self):
        """Return shift code and name for admin readability."""
        return f"{self.code} - {self.name}"
