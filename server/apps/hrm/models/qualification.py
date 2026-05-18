from django.db import models
from coresite.mixin.abstracttimestemp_model import AbstractTimeStampModel


class Qualification(AbstractTimeStampModel):
    """
    Qualification model - Global master data (NOT organization-specific).
    
    Inherits from AbstractTimeStampModel (NOT BaseModel) as qualifications are
    global reference data shared across all organizations.
    
    This is a system-wide master table that should be managed by super admins
    and used as reference data by all organizations (e.g., Bachelor's, Master's, PhD).
    
    Features:
    - Globally unique qualification names and codes
    - No tenant isolation (available to all organizations)
    - Active/inactive status tracking
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Qualification name (e.g., Bachelor's Degree, Master's Degree, PhD)"
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique qualification code (e.g., BS, MS, PHD, DIPLOMA)"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the qualification level and requirements"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this qualification is currently active"
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Qualification'
        verbose_name_plural = 'Qualifications'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        """Return qualification code and name for admin readability."""
        return f"{self.code} - {self.name}"
