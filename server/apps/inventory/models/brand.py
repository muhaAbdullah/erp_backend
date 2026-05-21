"""
Brand model for product manufacturer/brand information.
"""
from django.db import models
from coresite.mixin import BaseModel


class Brand(BaseModel):
    """
    Product brand/manufacturer information.
    
    Stores brand details for product categorization and tracking.
    All brands are organization-scoped for multi-tenant isolation.
    """
    
    name = models.CharField(
        max_length=100,
        help_text="Brand name (e.g., 'Samsung', 'Apple', 'Nike')"
    )
    
    code = models.CharField(
        max_length=50,
        help_text="Unique brand code for identification (e.g., 'SAMS', 'APPL')"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed description of the brand"
    )
    
    country = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Country of origin (e.g., 'South Korea', 'United States')"
    )
    
    website = models.URLField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Brand website URL"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this brand is active and available for use"
    )
    
    class Meta:
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        ordering = ['name']
        unique_together = [['organization', 'code']]
        indexes = [
            models.Index(fields=['organization', 'code']),
            models.Index(fields=['organization', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
