"""
Stock management business logic services.

All stock operations are atomic and create audit trail via StockMovement records.
"""
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from apps.inventory.models import (
    ProductStock, StockMovement, StockTransfer, StockAdjustment, Product, Warehouse
)
from apps.core.utils.audit_logger import log_action


@transaction.atomic
def complete_stock_transfer(transfer_id, user, request):
    """
    Execute a pending stock transfer atomically.
    
    Args:
        transfer_id: ID of the transfer to complete
        user: User executing the transfer
        request: HTTP request object for audit logging
    
    Returns:
        StockTransfer: The completed transfer
    
    Raises:
        ValidationError: If transfer is not in PENDING status
        ValidationError: If insufficient stock at source warehouse
    """
    from django.core.exceptions import ValidationError
    
    # Lock the transfer record
    transfer = StockTransfer.objects.select_for_update().get(pk=transfer_id)
    
    # Validate status
    if transfer.status != StockTransfer.PENDING:
        raise ValidationError(f'Transfer must be in PENDING status. Current status: {transfer.status}')
    
    # Get all items with product info
    items = transfer.items.select_related('product').all()
    
    if not items.exists():
        raise ValidationError('Transfer has no items.')
    
    # Validate stock availability and lock stock records
    for item in items:
        stock, created = ProductStock.objects.select_for_update().get_or_create(
            product=item.product,
            warehouse=transfer.source_warehouse,
            organization=transfer.organization,
            defaults={'quantity': Decimal('0.00'), 'reserved_quantity': Decimal('0.00')}
        )
        
        if stock.available_quantity < item.quantity:
            raise ValidationError(
                f'Insufficient stock for {item.product.code} at {transfer.source_warehouse.code}. '
                f'Available: {stock.available_quantity}, Required: {item.quantity}'
            )
    
    # Execute the transfer
    for item in items:
        # Decrease source warehouse stock
        source_stock = ProductStock.objects.select_for_update().get(
            product=item.product,
            warehouse=transfer.source_warehouse,
            organization=transfer.organization
        )
        source_stock.quantity -= item.quantity
        source_stock.save()
        
        # Create TRANSFER_OUT movement
        StockMovement.objects.create(
            product=item.product,
            warehouse=transfer.source_warehouse,
            movement_type=StockMovement.TRANSFER_OUT,
            quantity=-item.quantity,
            balance_after=source_stock.quantity,
            reference_type='StockTransfer',
            reference_id=transfer.id,
            reference_number=transfer.transfer_number,
            notes=f'Transfer to {transfer.destination_warehouse.code}',
            organization=transfer.organization
        )
        
        # Increase destination warehouse stock
        dest_stock, created = ProductStock.objects.select_for_update().get_or_create(
            product=item.product,
            warehouse=transfer.destination_warehouse,
            organization=transfer.organization,
            defaults={'quantity': Decimal('0.00'), 'reserved_quantity': Decimal('0.00')}
        )
        dest_stock.quantity += item.quantity
        dest_stock.save()
        
        # Create TRANSFER_IN movement
        StockMovement.objects.create(
            product=item.product,
            warehouse=transfer.destination_warehouse,
            movement_type=StockMovement.TRANSFER_IN,
            quantity=item.quantity,
            balance_after=dest_stock.quantity,
            reference_type='StockTransfer',
            reference_id=transfer.id,
            reference_number=transfer.transfer_number,
            notes=f'Transfer from {transfer.source_warehouse.code}',
            organization=transfer.organization
        )
    
    # Update transfer status
    transfer.status = StockTransfer.COMPLETED
    transfer.completed_at = timezone.now()
    transfer.completed_by = user
    transfer.save()
    
    # Audit log
    log_action(
        user=user,
        action='COMPLETE',
        model_name='StockTransfer',
        object_id=transfer.id,
        changes={'transfer_number': transfer.transfer_number, 'status': 'COMPLETED'},
        request=request
    )
    
    return transfer


@transaction.atomic
def approve_stock_adjustment(adjustment_id, user, request):
    """
    Approve and execute a pending stock adjustment atomically.
    
    Args:
        adjustment_id: ID of the adjustment to approve
        user: User approving the adjustment
        request: HTTP request object for audit logging
    
    Returns:
        StockAdjustment: The approved adjustment
    
    Raises:
        ValidationError: If adjustment is not in PENDING status
        ValidationError: If adjustment would result in negative stock
    """
    from django.core.exceptions import ValidationError
    
    # Lock the adjustment record
    adjustment = StockAdjustment.objects.select_for_update().get(pk=adjustment_id)
    
    # Validate status
    if adjustment.status != StockAdjustment.PENDING:
        raise ValidationError(f'Adjustment must be in PENDING status. Current status: {adjustment.status}')
    
    # Get all items with product info
    items = adjustment.items.select_related('product').all()
    
    if not items.exists():
        raise ValidationError('Adjustment has no items.')
    
    # Validate stock availability for removals
    for item in items:
        if item.quantity_change < 0:  # Removal
            stock, created = ProductStock.objects.select_for_update().get_or_create(
                product=item.product,
                warehouse=adjustment.warehouse,
                organization=adjustment.organization,
                defaults={'quantity': Decimal('0.00'), 'reserved_quantity': Decimal('0.00')}
            )
            
            if stock.quantity + item.quantity_change < 0:
                raise ValidationError(
                    f'Insufficient stock for {item.product.code}. '
                    f'Current: {stock.quantity}, Change: {item.quantity_change}'
                )
    
    # Execute the adjustment
    for item in items:
        # Get or create stock record
        stock, created = ProductStock.objects.select_for_update().get_or_create(
            product=item.product,
            warehouse=adjustment.warehouse,
            organization=adjustment.organization,
            defaults={'quantity': Decimal('0.00'), 'reserved_quantity': Decimal('0.00')}
        )
        
        # Update quantity
        stock.quantity += item.quantity_change
        stock.save()
        
        # Determine movement type
        if item.quantity_change > 0:
            movement_type = StockMovement.ADJUSTMENT_ADD
            quantity = item.quantity_change
        else:
            movement_type = StockMovement.ADJUSTMENT_REMOVE
            quantity = item.quantity_change
        
        # Create movement record
        StockMovement.objects.create(
            product=item.product,
            warehouse=adjustment.warehouse,
            movement_type=movement_type,
            quantity=quantity,
            balance_after=stock.quantity,
            reference_type='StockAdjustment',
            reference_id=adjustment.id,
            reference_number=adjustment.adjustment_number,
            notes=f'{adjustment.get_reason_display()}: {item.notes or ""}',
            organization=adjustment.organization
        )
    
    # Update adjustment status
    adjustment.status = StockAdjustment.APPROVED
    adjustment.approved_at = timezone.now()
    adjustment.approved_by = user
    adjustment.save()
    
    # Audit log
    log_action(
        user=user,
        action='APPROVE',
        model_name='StockAdjustment',
        object_id=adjustment.id,
        changes={'adjustment_number': adjustment.adjustment_number, 'status': 'APPROVED'},
        request=request
    )
    
    return adjustment


@transaction.atomic
def reject_stock_adjustment(adjustment_id, user, request, reason=None):
    """
    Reject a pending stock adjustment.
    
    Args:
        adjustment_id: ID of the adjustment to reject
        user: User rejecting the adjustment
        request: HTTP request object for audit logging
        reason: Optional reason for rejection
    
    Returns:
        StockAdjustment: The rejected adjustment
    
    Raises:
        ValidationError: If adjustment is not in PENDING status
    """
    from django.core.exceptions import ValidationError
    
    adjustment = StockAdjustment.objects.select_for_update().get(pk=adjustment_id)
    
    # Validate status
    if adjustment.status != StockAdjustment.PENDING:
        raise ValidationError(f'Adjustment must be in PENDING status. Current status: {adjustment.status}')
    
    # Update adjustment status
    adjustment.status = StockAdjustment.REJECTED
    if reason:
        adjustment.notes = f"{adjustment.notes or ''}\nRejection reason: {reason}".strip()
    adjustment.save()
    
    # Audit log
    log_action(
        user=user,
        action='REJECT',
        model_name='StockAdjustment',
        object_id=adjustment.id,
        changes={'adjustment_number': adjustment.adjustment_number, 'status': 'REJECTED'},
        request=request
    )
    
    return adjustment


@transaction.atomic
def add_opening_balance(product, warehouse, quantity, user, organization, reference_number=None):
    """
    Set opening balance for a product in a warehouse.
    
    Args:
        product: Product instance
        warehouse: Warehouse instance
        quantity: Opening quantity
        user: User creating the opening balance
        organization: Organization instance
        reference_number: Optional reference number
    
    Returns:
        ProductStock: The created/updated stock record
    """
    # Get or create stock record
    stock, created = ProductStock.objects.get_or_create(
        product=product,
        warehouse=warehouse,
        organization=organization,
        defaults={'quantity': quantity, 'reserved_quantity': Decimal('0.00')}
    )
    
    if not created:
        stock.quantity = quantity
        stock.save()
    
    # Create opening movement
    StockMovement.objects.create(
        product=product,
        warehouse=warehouse,
        movement_type=StockMovement.OPENING,
        quantity=quantity,
        balance_after=stock.quantity,
        reference_type='Opening',
        reference_number=reference_number or 'OPENING',
        notes='Opening balance',
        organization=organization
    )
    
    return stock


@transaction.atomic
def record_purchase(product, warehouse, quantity, reference_number, user, organization, notes=None):
    """
    Record a purchase (stock increase).
    
    Args:
        product: Product instance
        warehouse: Warehouse instance
        quantity: Quantity purchased
        reference_number: Purchase order number
        user: User recording the purchase
        organization: Organization instance
        notes: Optional notes
    
    Returns:
        ProductStock: Updated stock record
    """
    # Get or create stock record
    stock, created = ProductStock.objects.get_or_create(
        product=product,
        warehouse=warehouse,
        organization=organization,
        defaults={'quantity': Decimal('0.00'), 'reserved_quantity': Decimal('0.00')}
    )
    
    # Increase quantity
    stock.quantity += quantity
    stock.save()
    
    # Create purchase movement
    StockMovement.objects.create(
        product=product,
        warehouse=warehouse,
        movement_type=StockMovement.PURCHASE,
        quantity=quantity,
        balance_after=stock.quantity,
        reference_type='PurchaseOrder',
        reference_number=reference_number,
        notes=notes or 'Purchase received',
        organization=organization
    )
    
    return stock


@transaction.atomic
def record_sale(product, warehouse, quantity, reference_number, user, organization, notes=None):
    """
    Record a sale (stock decrease).
    
    Args:
        product: Product instance
        warehouse: Warehouse instance
        quantity: Quantity sold
        reference_number: Sales order number
        user: User recording the sale
        organization: Organization instance
        notes: Optional notes
    
    Returns:
        ProductStock: Updated stock record
    
    Raises:
        ValidationError: If insufficient stock available
    """
    from django.core.exceptions import ValidationError
    
    # Get stock record
    try:
        stock = ProductStock.objects.select_for_update().get(
            product=product,
            warehouse=warehouse,
            organization=organization
        )
    except ProductStock.DoesNotExist:
        raise ValidationError(f'No stock record found for {product.code} at {warehouse.code}')
    
    # Check available quantity
    if stock.available_quantity < quantity:
        raise ValidationError(
            f'Insufficient stock for {product.code} at {warehouse.code}. '
            f'Available: {stock.available_quantity}, Required: {quantity}'
        )
    
    # Decrease quantity
    stock.quantity -= quantity
    stock.save()
    
    # Create sale movement
    StockMovement.objects.create(
        product=product,
        warehouse=warehouse,
        movement_type=StockMovement.SALE,
        quantity=-quantity,
        balance_after=stock.quantity,
        reference_type='SalesOrder',
        reference_number=reference_number,
        notes=notes or 'Sale',
        organization=organization
    )
    
    return stock


def get_low_stock_products(organization):
    """
    Get products with stock below reorder level.
    
    Args:
        organization: Organization instance
    
    Returns:
        QuerySet: Products below reorder level with stock info
    """
    from django.db.models import Sum, F
    
    # Get products with total stock below reorder level
    products = Product.objects.filter(
        organization=organization,
        is_active=True
    ).annotate(
        total_stock=Sum('stock_records__quantity')
    ).filter(
        total_stock__lt=F('reorder_level')
    ).select_related('category', 'brand', 'unit')
    
    return products
