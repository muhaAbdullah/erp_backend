"""
Unit model for measurement units.
"""
from django.db import models
from coresite.mixin import BaseModel


class Unit(BaseModel):
    """
    Unit of measurement for products.
    
    Defines how products are measured and quantified (e.g., pieces, kg, liters).
    All units are organization-scoped for multi-tenant isolation.
    """
    
    name = models.CharField(
        max_length=100,
        help_text="Full unit name (e.g., 'Kilogram', 'Piece', 'Liter')"
    )
    
    code = models.CharField(
        max_length=50,
        help_text="Unique unit code for identification (e.g., 'KG', 'PCS', 'LTR')"
    )
    
    symbol = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="Unit symbol for display (e.g., 'kg', 'pcs', 'L')"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed description of the unit"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this unit is active and available for use"
    )
    
    class Meta:
        verbose_name = 'Unit'
        verbose_name_plural = 'Units'
        ordering = ['name']
        unique_together = [['organization', 'code']]
        indexes = [
            models.Index(fields=['organization', 'code']),
            models.Index(fields=['organization', 'is_active']),
        ]
    
    def __str__(self):
        if self.symbol:
            return f"{self.name} ({self.symbol})"
        return self.name
