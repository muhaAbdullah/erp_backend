from django.db import models
from coresite.mixin.abstracttimestemp_model import AbstractTimeStampModel


class Religion(AbstractTimeStampModel):
    """
    Religion model - Global master data (NOT organization-specific).
    
    Inherits from AbstractTimeStampModel (NOT BaseModel) as religions are
    global reference data shared across all organizations.
    
    This is a system-wide master table that should be managed by super admins
    and used as reference data by all organizations.
    
    Features:
    - Globally unique religion names
    - No tenant isolation (available to all organizations)
    - Active/inactive status tracking
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Religion name (e.g., Islam, Christianity, Hinduism, Buddhism)"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description or notes about the religion"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this religion option is currently active"
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Religion'
        verbose_name_plural = 'Religions'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        """Return religion name for admin readability."""
        return self.name
