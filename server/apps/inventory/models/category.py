"""
Category model for product categorization with hierarchical structure.
"""
from django.db import models
from django.core.exceptions import ValidationError
from coresite.mixin import BaseModel


class Category(BaseModel):
    """
    Product category with hierarchical parent-child relationships.
    
    Supports multi-level category trees (e.g., Electronics > Computers > Laptops).
    All categories are organization-scoped for multi-tenant isolation.
    """
    
    name = models.CharField(
        max_length=100,
        help_text="Category name (e.g., 'Electronics', 'Furniture')"
    )
    
    code = models.CharField(
        max_length=50,
        help_text="Unique category code for identification (e.g., 'ELEC', 'FURN')"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed description of the category"
    )
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        null=True,
        blank=True,
        help_text="Parent category for hierarchical organization"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this category is active and available for use"
    )
    
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['name']
        unique_together = [['organization', 'code']]
        indexes = [
            models.Index(fields=['organization', 'code']),
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['organization', 'parent']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def clean(self):
        """
        Validate category data before saving.
        - Prevents circular parent relationships
        - Ensures parent belongs to same organization
        """
        super().clean()
        
        # Validate parent belongs to same organization
        if self.parent and self.parent.organization != self.organization:
            raise ValidationError({
                'parent': 'Parent category must belong to the same organization.'
            })
        
        # Prevent circular parent relationships
        if self.parent and self.pk:
            current = self.parent
            while current:
                if current.pk == self.pk:
                    raise ValidationError({
                        'parent': 'Circular parent relationship detected. A category cannot be its own ancestor.'
                    })
                current = current.parent
    
    def save(self, *args, **kwargs):
        """Call clean before saving."""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_full_path(self):
        """
        Get the full hierarchical path of the category.
        
        Returns:
            String representing the full path (e.g., "Electronics > Computers > Laptops")
        """
        path = [self.name]
        current = self.parent
        
        while current:
            path.insert(0, current.name)
            current = current.parent
        
        return ' > '.join(path)
    
    def get_descendants(self):
        """
        Get all descendant categories (children, grandchildren, etc.).
        
        Returns:
            QuerySet of all descendant categories
        """
        descendants = list(self.children.all())
        for child in list(descendants):
            descendants.extend(child.get_descendants())
        return descendants
