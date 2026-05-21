"""
Product model for inventory items.
"""
from django.db import models
from django.core.exceptions import ValidationError
from coresite.mixin import BaseModel


class Product(BaseModel):
    """
    Product/Item master data.
    
    Core product information including pricing, categorization, and stock settings.
    All products are organization-scoped for multi-tenant isolation.
    """
    
    # Product Type Choices
    GOODS = 'GOODS'
    SERVICE = 'SERVICE'
    CONSUMABLE = 'CONSUMABLE'
    
    PRODUCT_TYPE_CHOICES = [
        (GOODS, 'Goods'),
        (SERVICE, 'Service'),
        (CONSUMABLE, 'Consumable'),
    ]
    
    # Basic Information
    name = models.CharField(
        max_length=200,
        help_text="Product name"
    )
    
    code = models.CharField(
        max_length=50,
        help_text="Unique product code/SKU (e.g., 'PRD-001')"
    )
    
    barcode = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Product barcode (EAN, UPC, etc.)"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed product description"
    )
    
    # Classification
    product_type = models.CharField(
        max_length=20,
        choices=PRODUCT_TYPE_CHOICES,
        default=GOODS,
        help_text="Type of product (affects inventory tracking)"
    )
    
    category = models.ForeignKey(
        'inventory.Category',
        on_delete=models.PROTECT,
        related_name='products',
        null=True,
        blank=True,
        help_text="Product category"
    )
    
    brand = models.ForeignKey(
        'inventory.Brand',
        on_delete=models.PROTECT,
        related_name='products',
        null=True,
        blank=True,
        help_text="Product brand/manufacturer"
    )
    
    unit = models.ForeignKey(
        'inventory.Unit',
        on_delete=models.PROTECT,
        related_name='products',
        help_text="Unit of measurement"
    )
    
    # Pricing
    cost_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Cost price per unit (purchase price)"
    )
    
    selling_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Selling price per unit"
    )
    
    # Stock Management
    reorder_level = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Stock level at which to reorder"
    )
    
    reorder_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Quantity to order when restocking"
    )
    
    # Status Flags
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this product is active"
    )
    
    can_be_sold = models.BooleanField(
        default=True,
        help_text="Whether this product can be sold"
    )
    
    can_be_purchased = models.BooleanField(
        default=True,
        help_text="Whether this product can be purchased"
    )
    
    # Additional Notes
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes or comments"
    )
    
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['name']
        unique_together = [['organization', 'code']]
        indexes = [
            models.Index(fields=['organization', 'code']),
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['organization', 'category']),
            models.Index(fields=['organization', 'brand']),
            models.Index(fields=['organization', 'barcode']),
            models.Index(fields=['product_type']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def clean(self):
        """
        Validate product data before saving.
        - Ensures category, brand, and unit belong to same organization
        - Validates pricing
        """
        super().clean()
        
        # Validate category belongs to same organization
        if self.category and self.category.organization != self.organization:
            raise ValidationError({
                'category': 'Category must belong to the same organization.'
            })
        
        # Validate brand belongs to same organization
        if self.brand and self.brand.organization != self.organization:
            raise ValidationError({
                'brand': 'Brand must belong to the same organization.'
            })
        
        # Validate unit belongs to same organization
        if self.unit and self.unit.organization != self.organization:
            raise ValidationError({
                'unit': 'Unit must belong to the same organization.'
            })
        
        # Validate pricing
        if self.cost_price < 0:
            raise ValidationError({
                'cost_price': 'Cost price cannot be negative.'
            })
        
        if self.selling_price < 0:
            raise ValidationError({
                'selling_price': 'Selling price cannot be negative.'
            })
        
        # Validate reorder levels
        if self.reorder_level < 0:
            raise ValidationError({
                'reorder_level': 'Reorder level cannot be negative.'
            })
        
        if self.reorder_quantity < 0:
            raise ValidationError({
                'reorder_quantity': 'Reorder quantity cannot be negative.'
            })
    
    def save(self, *args, **kwargs):
        """Call clean before saving."""
        self.full_clean()
        super().save(*args, **kwargs)
