"""
Stock management models for inventory tracking.
"""
from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from coresite.mixin import BaseModel


class ProductStock(BaseModel):
    """
    Current stock levels for products in warehouses.
    
    Maintains real-time inventory quantities per product per warehouse.
    Uses atomic transactions to prevent race conditions.
    """
    
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.CASCADE,
        related_name='stock_records',
        help_text="Product being tracked"
    )
    
    warehouse = models.ForeignKey(
        'inventory.Warehouse',
        on_delete=models.CASCADE,
        related_name='stock_records',
        help_text="Warehouse location"
    )
    
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Current quantity in stock"
    )
    
    reserved_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Quantity reserved for pending orders"
    )
    
    class Meta:
        verbose_name = 'Product Stock'
        verbose_name_plural = 'Product Stocks'
        unique_together = [['organization', 'product', 'warehouse']]
        indexes = [
            models.Index(fields=['organization', 'product']),
            models.Index(fields=['organization', 'warehouse']),
            models.Index(fields=['organization', 'product', 'warehouse']),
        ]
    
    def __str__(self):
        return f"{self.product.code} @ {self.warehouse.code}: {self.quantity}"
    
    @property
    def available_quantity(self):
        """Calculate available quantity (total - reserved)."""
        return self.quantity - self.reserved_quantity
    
    def clean(self):
        """
        Validate stock data before saving.
        - Quantity cannot be negative
        - Reserved quantity cannot exceed total quantity
        - Product and warehouse must belong to same organization
        """
        super().clean()
        
        # Validate quantity is not negative
        if self.quantity < 0:
            raise ValidationError({
                'quantity': 'Quantity cannot be negative.'
            })
        
        # Validate reserved quantity
        if self.reserved_quantity < 0:
            raise ValidationError({
                'reserved_quantity': 'Reserved quantity cannot be negative.'
            })
        
        if self.reserved_quantity > self.quantity:
            raise ValidationError({
                'reserved_quantity': 'Reserved quantity cannot exceed total quantity.'
            })
        
        # Validate product belongs to same organization
        if self.product and self.product.organization != self.organization:
            raise ValidationError({
                'product': 'Product must belong to the same organization.'
            })
        
        # Validate warehouse belongs to same organization
        if self.warehouse and self.warehouse.organization != self.organization:
            raise ValidationError({
                'warehouse': 'Warehouse must belong to the same organization.'
            })
    
    def save(self, *args, **kwargs):
        """Call clean before saving."""
        self.full_clean()
        super().save(*args, **kwargs)


class StockMovement(BaseModel):
    """
    Immutable audit trail of all stock changes.
    
    Every stock operation creates a movement record for complete traceability.
    Records are never updated or deleted (append-only log).
    """
    
    # Movement Type Choices
    PURCHASE = 'PURCHASE'
    SALE = 'SALE'
    TRANSFER_IN = 'TRANSFER_IN'
    TRANSFER_OUT = 'TRANSFER_OUT'
    ADJUSTMENT_ADD = 'ADJUSTMENT_ADD'
    ADJUSTMENT_REMOVE = 'ADJUSTMENT_REMOVE'
    RETURN = 'RETURN'
    DAMAGE = 'DAMAGE'
    OPENING = 'OPENING'
    
    MOVEMENT_TYPE_CHOICES = [
        (PURCHASE, 'Purchase'),
        (SALE, 'Sale'),
        (TRANSFER_IN, 'Transfer In'),
        (TRANSFER_OUT, 'Transfer Out'),
        (ADJUSTMENT_ADD, 'Adjustment - Add'),
        (ADJUSTMENT_REMOVE, 'Adjustment - Remove'),
        (RETURN, 'Return'),
        (DAMAGE, 'Damage/Loss'),
        (OPENING, 'Opening Balance'),
    ]
    
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.CASCADE,
        related_name='stock_movements',
        help_text="Product that moved"
    )
    
    warehouse = models.ForeignKey(
        'inventory.Warehouse',
        on_delete=models.CASCADE,
        related_name='stock_movements',
        help_text="Warehouse where movement occurred"
    )
    
    movement_type = models.CharField(
        max_length=20,
        choices=MOVEMENT_TYPE_CHOICES,
        help_text="Type of stock movement"
    )
    
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Quantity moved (positive or negative)"
    )
    
    balance_after = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Stock balance after this movement"
    )
    
    reference_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Type of reference document (e.g., 'StockTransfer', 'PurchaseOrder')"
    )
    
    reference_id = models.IntegerField(
        blank=True,
        null=True,
        help_text="ID of the reference document"
    )
    
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Reference document number"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about the movement"
    )
    
    movement_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time of the movement"
    )
    
    class Meta:
        verbose_name = 'Stock Movement'
        verbose_name_plural = 'Stock Movements'
        ordering = ['-movement_date']
        indexes = [
            models.Index(fields=['organization', 'product']),
            models.Index(fields=['organization', 'warehouse']),
            models.Index(fields=['organization', 'movement_type']),
            models.Index(fields=['organization', 'movement_date']),
            models.Index(fields=['-movement_date']),
        ]
    
    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.product.code} ({self.quantity})"


class StockTransfer(BaseModel):
    """
    Stock transfer between warehouses.
    
    Manages movement of inventory between different warehouse locations.
    Status-driven workflow: DRAFT -> PENDING -> COMPLETED or CANCELLED.
    """
    
    # Status Choices
    DRAFT = 'DRAFT'
    PENDING = 'PENDING'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'
    
    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
    ]
    
    transfer_number = models.CharField(
        max_length=50,
        help_text="Unique transfer reference number"
    )
    
    source_warehouse = models.ForeignKey(
        'inventory.Warehouse',
        on_delete=models.PROTECT,
        related_name='outgoing_transfers',
        help_text="Warehouse stock is transferred from"
    )
    
    destination_warehouse = models.ForeignKey(
        'inventory.Warehouse',
        on_delete=models.PROTECT,
        related_name='incoming_transfers',
        help_text="Warehouse stock is transferred to"
    )
    
    transfer_date = models.DateField(
        help_text="Date of the transfer"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=DRAFT,
        help_text="Current status of the transfer"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about the transfer"
    )
    
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date and time when transfer was completed"
    )
    
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='completed_transfers',
        help_text="User who completed the transfer"
    )
    
    class Meta:
        verbose_name = 'Stock Transfer'
        verbose_name_plural = 'Stock Transfers'
        ordering = ['-transfer_date']
        unique_together = [['organization', 'transfer_number']]
        indexes = [
            models.Index(fields=['organization', 'transfer_number']),
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['organization', 'source_warehouse']),
            models.Index(fields=['organization', 'destination_warehouse']),
            models.Index(fields=['-transfer_date']),
        ]
    
    def __str__(self):
        return f"{self.transfer_number} - {self.source_warehouse.code} → {self.destination_warehouse.code}"
    
    def clean(self):
        """
        Validate transfer data before saving.
        - Source and destination must be different
        - Both warehouses must belong to same organization
        """
        super().clean()
        
        # Validate warehouses are different
        if self.source_warehouse and self.destination_warehouse:
            if self.source_warehouse == self.destination_warehouse:
                raise ValidationError({
                    'destination_warehouse': 'Source and destination warehouses must be different.'
                })
        
        # Validate source warehouse belongs to same organization
        if self.source_warehouse and self.source_warehouse.organization != self.organization:
            raise ValidationError({
                'source_warehouse': 'Source warehouse must belong to the same organization.'
            })
        
        # Validate destination warehouse belongs to same organization
        if self.destination_warehouse and self.destination_warehouse.organization != self.organization:
            raise ValidationError({
                'destination_warehouse': 'Destination warehouse must belong to the same organization.'
            })
    
    def save(self, *args, **kwargs):
        """Call clean before saving."""
        self.full_clean()
        super().save(*args, **kwargs)


class StockTransferItem(BaseModel):
    """
    Line items for stock transfers.
    
    Each item represents a specific product and quantity being transferred.
    """
    
    transfer = models.ForeignKey(
        'inventory.StockTransfer',
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Parent transfer record"
    )
    
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.PROTECT,
        related_name='transfer_items',
        help_text="Product being transferred"
    )
    
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Quantity to transfer"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Notes about this item"
    )
    
    class Meta:
        verbose_name = 'Stock Transfer Item'
        verbose_name_plural = 'Stock Transfer Items'
        indexes = [
            models.Index(fields=['organization', 'transfer']),
            models.Index(fields=['organization', 'product']),
        ]
    
    def __str__(self):
        return f"{self.transfer.transfer_number} - {self.product.code} ({self.quantity})"
    
    def clean(self):
        """
        Validate transfer item data before saving.
        - Quantity must be positive
        - Product must belong to same organization
        """
        super().clean()
        
        # Validate quantity is positive
        if self.quantity <= 0:
            raise ValidationError({
                'quantity': 'Quantity must be greater than zero.'
            })
        
        # Validate product belongs to same organization
        if self.product and self.product.organization != self.organization:
            raise ValidationError({
                'product': 'Product must belong to the same organization.'
            })
    
    def save(self, *args, **kwargs):
        """Call clean before saving."""
        self.full_clean()
        super().save(*args, **kwargs)


class StockAdjustment(BaseModel):
    """
    Stock quantity adjustments for corrections.
    
    Handles inventory corrections for damage, loss, found items, etc.
    Requires approval workflow: DRAFT -> PENDING -> APPROVED/REJECTED.
    """
    
    # Reason Choices
    DAMAGE = 'DAMAGE'
    LOSS = 'LOSS'
    FOUND = 'FOUND'
    CORRECTION = 'CORRECTION'
    EXPIRY = 'EXPIRY'
    QUALITY = 'QUALITY'
    OTHER = 'OTHER'
    
    REASON_CHOICES = [
        (DAMAGE, 'Damage'),
        (LOSS, 'Loss/Theft'),
        (FOUND, 'Found Items'),
        (CORRECTION, 'Inventory Correction'),
        (EXPIRY, 'Expiry'),
        (QUALITY, 'Quality Issues'),
        (OTHER, 'Other'),
    ]
    
    # Status Choices
    DRAFT = 'DRAFT'
    PENDING = 'PENDING'
    APPROVED = 'APPROVED'
    REJECTED = 'REJECTED'
    
    STATUS_CHOICES = [
        (DRAFT, 'Draft'),
        (PENDING, 'Pending Approval'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
    ]
    
    adjustment_number = models.CharField(
        max_length=50,
        help_text="Unique adjustment reference number"
    )
    
    warehouse = models.ForeignKey(
        'inventory.Warehouse',
        on_delete=models.PROTECT,
        related_name='adjustments',
        help_text="Warehouse where adjustment occurs"
    )
    
    adjustment_date = models.DateField(
        help_text="Date of the adjustment"
    )
    
    reason = models.CharField(
        max_length=20,
        choices=REASON_CHOICES,
        help_text="Reason for the adjustment"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=DRAFT,
        help_text="Current status of the adjustment"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about the adjustment"
    )
    
    approved_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date and time when adjustment was approved"
    )
    
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_adjustments',
        help_text="User who approved the adjustment"
    )
    
    class Meta:
        verbose_name = 'Stock Adjustment'
        verbose_name_plural = 'Stock Adjustments'
        ordering = ['-adjustment_date']
        unique_together = [['organization', 'adjustment_number']]
        indexes = [
            models.Index(fields=['organization', 'adjustment_number']),
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['organization', 'warehouse']),
            models.Index(fields=['-adjustment_date']),
        ]
    
    def __str__(self):
        return f"{self.adjustment_number} - {self.warehouse.code} ({self.get_status_display()})"
    
    def clean(self):
        """
        Validate adjustment data before saving.
        - Warehouse must belong to same organization
        """
        super().clean()
        
        # Validate warehouse belongs to same organization
        if self.warehouse and self.warehouse.organization != self.organization:
            raise ValidationError({
                'warehouse': 'Warehouse must belong to the same organization.'
            })
    
    def save(self, *args, **kwargs):
        """Call clean before saving."""
        self.full_clean()
        super().save(*args, **kwargs)


class StockAdjustmentItem(BaseModel):
    """
    Line items for stock adjustments.
    
    Each item represents a specific product and quantity change.
    Supports both positive (add) and negative (remove) adjustments.
    """
    
    adjustment = models.ForeignKey(
        'inventory.StockAdjustment',
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Parent adjustment record"
    )
    
    product = models.ForeignKey(
        'inventory.Product',
        on_delete=models.PROTECT,
        related_name='adjustment_items',
        help_text="Product being adjusted"
    )
    
    quantity_change = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Quantity change (positive = add, negative = remove)"
    )
    
    current_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Current quantity before adjustment"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Notes about this item adjustment"
    )
    
    class Meta:
        verbose_name = 'Stock Adjustment Item'
        verbose_name_plural = 'Stock Adjustment Items'
        indexes = [
            models.Index(fields=['organization', 'adjustment']),
            models.Index(fields=['organization', 'product']),
        ]
    
    def __str__(self):
        return f"{self.adjustment.adjustment_number} - {self.product.code} ({self.quantity_change:+})"
    
    @property
    def new_quantity(self):
        """Calculate new quantity after adjustment."""
        return self.current_quantity + self.quantity_change
    
    def clean(self):
        """
        Validate adjustment item data before saving.
        - Quantity change cannot be zero
        - New quantity cannot be negative
        - Product must belong to same organization
        """
        super().clean()
        
        # Validate quantity change is not zero
        if self.quantity_change == 0:
            raise ValidationError({
                'quantity_change': 'Quantity change cannot be zero.'
            })
        
        # Validate new quantity is not negative
        if self.new_quantity < 0:
            raise ValidationError({
                'quantity_change': f'Adjustment would result in negative stock. Current: {self.current_quantity}, Change: {self.quantity_change}'
            })
        
        # Validate product belongs to same organization
        if self.product and self.product.organization != self.organization:
            raise ValidationError({
                'product': 'Product must belong to the same organization.'
            })
    
    def save(self, *args, **kwargs):
        """Call clean before saving."""
        self.full_clean()
        super().save(*args, **kwargs)
