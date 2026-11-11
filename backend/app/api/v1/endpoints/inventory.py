from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.db.models import InventoryItem, InventoryLot
from backend.app.domain.fefo_dispenser import (
    dispense_item_fefo,
    quarantine_expired_lots,
    InsufficientStockError
)
from backend.app.domain.equipment_tracker import calculate_equipment_and_oxygen_metrics
from backend.app.schemas.resource import (
    InventoryItemResponse,
    InventoryLotResponse,
    DispenseRequest,
    DispenseResponse,
    EquipmentMetricsResponse
)

router = APIRouter()


@router.get("/items", response_model=List[InventoryItemResponse])
def list_inventory_items(
    category: Optional[str] = None,
    low_stock_only: bool = False,
    db: Session = Depends(get_db)
):
    """
    Module 3: Returns inventory catalog with total usable non-expired stock and reorder status.
    """
    # Run automatic quarantine check first
    quarantine_expired_lots(db)

    query = db.query(InventoryItem)
    if category:
        query = query.filter(InventoryItem.category == category)

    items = query.all()
    today = date.today()
    results = []

    for item in items:
        # Usable stock: non-quarantined and not expired
        usable_lots = [
            l for l in item.lots
            if not l.is_quarantined and l.expiry_date >= today
        ]
        total_usable = sum(l.quantity_on_hand for l in usable_lots)
        reorder_needed = total_usable <= item.reorder_threshold

        if low_stock_only and not reorder_needed:
            continue

        results.append(
            InventoryItemResponse(
                id=item.id,
                sku_code=item.sku_code,
                generic_name=item.generic_name,
                category=item.category,
                unit_of_measure=item.unit_of_measure,
                reorder_threshold=item.reorder_threshold,
                target_stock_level=item.target_stock_level,
                standard_lead_time_days=item.standard_lead_time_days,
                total_usable_stock=total_usable,
                reorder_required=reorder_needed,
                active_lots=[InventoryLotResponse.model_validate(l) for l in usable_lots]
            )
        )

    return results


@router.get("/lots", response_model=List[InventoryLotResponse])
def list_inventory_lots(
    sku_code: Optional[str] = None,
    include_quarantined: bool = False,
    db: Session = Depends(get_db)
):
    """
    Module 3: Lists inventory lots sorted by expiry date ASC (FEFO priority order).
    """
    query = db.query(InventoryLot)
    if sku_code:
        item = db.query(InventoryItem).filter(InventoryItem.sku_code == sku_code).first()
        if item:
            query = query.filter(InventoryLot.item_id == item.id)
    if not include_quarantined:
        query = query.filter(InventoryLot.is_quarantined == False)

    lots = query.order_by(InventoryLot.expiry_date.asc()).all()
    return lots


@router.post("/dispense", response_model=DispenseResponse)
def dispense_medication_fefo(
    payload: DispenseRequest,
    db: Session = Depends(get_db)
):
    """
    Module 3: Executes First Expiry, First Out (FEFO) dispensing for requested SKU.
    Deducts stock from nearest-expiring batches first and records audit movements.
    """
    try:
        result = dispense_item_fefo(
            db=db,
            sku_code=payload.sku_code,
            requested_qty=payload.requested_qty,
            dispensed_by=payload.dispensed_by,
            reason=payload.reason or "Prescription dispensing"
        )
        return DispenseResponse(**result)
    except InsufficientStockError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err)
        )
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(err)
        )


@router.get("/equipment-telemetry", response_model=EquipmentMetricsResponse)
def get_equipment_and_oxygen_telemetry(db: Session = Depends(get_db)):
    """
    Module 3: Real-time telemetry for ventilator fleet utilization and oxygen days-of-supply.
    """
    data = calculate_equipment_and_oxygen_metrics(db)
    return EquipmentMetricsResponse(**data)
