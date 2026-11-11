"""
Module 3: First Expiry, First Out (FEFO) dispensing engine and stockout risk calculator.
Ensures pharmaceutical lots are dispensed in strict ascending order of expiry dates,
quarantines expired lots, and produces stock replenishment alerts.
"""

from datetime import date, datetime
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from backend.app.db.models import InventoryItem, InventoryLot, StockMovement


class InsufficientStockError(ValueError):
    """Raised when the requested dispense quantity exceeds usable stock."""
    pass


class ExpiredStockError(ValueError):
    """Raised when an attempt is made to dispense an expired or quarantined lot."""
    pass


def quarantine_expired_lots(db: Session, reference_date: date = None) -> int:
    """
    Scans inventory lots and marks lots past their expiration date as quarantined.
    Returns count of newly quarantined lots.
    """
    if reference_date is None:
        reference_date = date.today()

    expired_lots = (
        db.query(InventoryLot)
        .filter(
            InventoryLot.expiry_date < reference_date,
            InventoryLot.is_quarantined == False,
            InventoryLot.quantity_on_hand > 0
        )
        .all()
    )

    for lot in expired_lots:
        lot.is_quarantined = True
        movement = StockMovement(
            item_id=lot.item_id,
            lot_id=lot.id,
            movement_type="EXPIRED_DISCARD",
            quantity=lot.quantity_on_hand,
            reason=f"Automatic FEFO quarantine: expired on {lot.expiry_date.isoformat()}",
            recorded_at=datetime.utcnow(),
            recorded_by="FEFO_SYSTEM"
        )
        db.add(movement)

    if expired_lots:
        db.commit()

    return len(expired_lots)


def dispense_item_fefo(
    db: Session,
    sku_code: str,
    requested_qty: int,
    dispensed_by: str = "PHARMACY_STAFF",
    reason: str = "Patient prescription dispensation"
) -> Dict[str, Any]:
    """
    Executes First Expiry, First Out (FEFO) dispensing:
    1. Fetches item by SKU.
    2. Retrieves active, non-quarantined lots sorted by expiry_date ASC.
    3. Validates total usable quantity >= requested_qty.
    4. Deducts quantity from earliest expiring lots sequentially.
    5. Records immutable StockMovement logs.
    """
    if requested_qty <= 0:
        raise ValueError("Dispense quantity must be strictly positive.")

    item = db.query(InventoryItem).filter(InventoryItem.sku_code == sku_code).first()
    if not item:
        raise ValueError(f"Inventory SKU '{sku_code}' not found.")

    # Quarantine any expired stock before calculating available quantity
    quarantine_expired_lots(db)

    # Fetch active, non-expired lots in FEFO order (expiry_date ASC)
    active_lots = (
        db.query(InventoryLot)
        .filter(
            InventoryLot.item_id == item.id,
            InventoryLot.is_quarantined == False,
            InventoryLot.quantity_on_hand > 0,
            InventoryLot.expiry_date >= date.today()
        )
        .order_by(InventoryLot.expiry_date.asc())
        .all()
    )

    total_available = sum(lot.quantity_on_hand for lot in active_lots)
    if total_available < requested_qty:
        raise InsufficientStockError(
            f"Insufficient usable stock for SKU '{sku_code}'. "
            f"Requested: {requested_qty}, Usable on hand: {total_available}."
        )

    remaining_to_dispense = requested_qty
    dispensed_allocations = []

    for lot in active_lots:
        if remaining_to_dispense <= 0:
            break

        take_qty = min(lot.quantity_on_hand, remaining_to_dispense)
        lot.quantity_on_hand -= take_qty
        remaining_to_dispense -= take_qty

        # Record audit movement
        movement = StockMovement(
            item_id=item.id,
            lot_id=lot.id,
            movement_type="DISPENSE",
            quantity=take_qty,
            reason=f"{reason} (Lot: {lot.lot_number}, Expiry: {lot.expiry_date.isoformat()})",
            recorded_at=datetime.utcnow(),
            recorded_by=dispensed_by
        )
        db.add(movement)

        dispensed_allocations.append({
            "lot_id": lot.id,
            "lot_number": lot.lot_number,
            "expiry_date": lot.expiry_date.isoformat(),
            "quantity_deducted": take_qty,
            "remaining_in_lot": lot.quantity_on_hand
        })

    db.commit()

    # Recalculate remaining usable stock
    new_total_stock = sum(
        l.quantity_on_hand for l in item.lots if not l.is_quarantined and l.expiry_date >= date.today()
    )
    is_low_stock = new_total_stock <= item.reorder_threshold

    return {
        "sku_code": item.sku_code,
        "generic_name": item.generic_name,
        "requested_qty": requested_qty,
        "dispensed_allocations": dispensed_allocations,
        "remaining_stock": new_total_stock,
        "reorder_threshold": item.reorder_threshold,
        "reorder_triggered": is_low_stock,
    }

