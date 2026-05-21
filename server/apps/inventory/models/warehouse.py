"""
Warehouse model for storage location management.
"""
from django.db import models
from coresite.mixin import BaseModel


class Warehouse(BaseModel):
    """
    Physical warehouse/storage location.
    
    Represents physical locations where inventory is stored.
    All warehouses are organization-scoped for multi-tenant isolation.
    """
    
    name = models.CharField(
        max_length=100,
        help_text="Warehouse name (e.g., 'Main Warehouse', 'Store #1')"
    )
    
    code = models.CharField(
        max_length=50,
        help_text="Unique warehouse code for identification (e.g., 'WH-MAIN', 'STR-01')"
    )
    
    address = models.TextField(
        blank=True,
        null=True,
        help_text="Full street address of the warehouse"
    )
    
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="City where warehouse is located"
    )
    
    state = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="State/Province where warehouse is located"
    )
    
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Country where warehouse is located"
    )
    
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Postal/ZIP code of the warehouse"
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Contact phone number"
    )
    
    email = models.EmailField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Contact email address"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this warehouse is active and available for use"
    )
    
    class Meta:
        verbose_name = 'Warehouse'
        verbose_name_plural = 'Warehouses'
        ordering = ['name']
        unique_together = [['organization', 'code']]
        indexes = [
            models.Index(fields=['organization', 'code']),
            models.Index(fields=['organization', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
