from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.db.models import Bed, Ward, BedStatusEvent, RosterAssignment
from backend.app.domain.bed_lifecycle import (
    BedState, validate_bed_transition, InvalidBedStateTransitionError
)
from backend.app.domain.capacity_calculator import calculate_ward_operational_capacity
from backend.app.schemas.hospital import BedResponse, BedStateUpdate, WardCapacitySummary

router = APIRouter()


@router.get("", response_model=List[BedResponse])
def list_all_beds(
    ward_id: str = None,
    current_state: str = None,
    db: Session = Depends(get_db)
):
    """
    Module 2: Lists all physical beds across wards with filtering support.
    """
    query = db.query(Bed)
    if ward_id:
        query = query.filter(Bed.ward_id == ward_id)
    if current_state:
        query = query.filter(Bed.current_state == current_state)
    return query.order_by(Bed.bed_number).all()


@router.patch("/{bed_id}/state", response_model=BedResponse)
def update_bed_state(
    bed_id: str,
    update: BedStateUpdate,
    db: Session = Depends(get_db)
):
    """
    Module 2: Transitions a bed's operational state with strict state-machine validation.
    Returns HTTP 422 Unprocessable Entity if transition is illegal.
    """
    bed = db.query(Bed).filter(Bed.id == bed_id).first()
    if not bed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Bed '{bed_id}' not found.")

    current_enum_state = BedState(bed.current_state)
    new_enum_state = update.new_state

    try:
        validate_bed_transition(from_state=current_enum_state, to_state=new_enum_state, bed_id=bed.bed_number)
    except InvalidBedStateTransitionError as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(err)
        )

    # Record event in immutable ledger
    event = BedStatusEvent(
        bed_id=bed.id,
        from_state=current_enum_state.value,
        to_state=new_enum_state.value,
        reason=update.reason or f"Operational transition to {new_enum_state.value}",
        recorded_by=update.operator_id,
        recorded_at=datetime.utcnow()
    )
    db.add(event)

    # Update bed state
    bed.current_state = new_enum_state.value
    bed.last_state_change = datetime.utcnow()
    db.commit()
    db.refresh(bed)

    return bed


@router.get("/capacity", response_model=List[WardCapacitySummary])
def get_operational_capacity_by_ward(db: Session = Depends(get_db)):
    """
    Module 2: Computes physical vs. operational (staffed) usable capacity per ward.
    Takes into account on-duty nurses and nurse-to-patient ratio limits.
    """
    wards = db.query(Ward).all()
    summaries = []

    for ward in wards:
        beds = db.query(Bed).filter(Bed.ward_id == ward.id).all()
        bed_dicts = [{"state": b.current_state} for b in beds]

        # Count active on-duty nurses for this ward
        on_duty_nurse_count = (
            db.query(RosterAssignment)
            .filter(
                RosterAssignment.ward_id == ward.id,
                RosterAssignment.role == "Nurse",
                RosterAssignment.is_on_duty == True
            )
            .count()
        )
        # Default fallback to 2 nurses if roster is unpopulated
        if on_duty_nurse_count == 0:
            on_duty_nurse_count = 2

        metrics = calculate_ward_operational_capacity(
            beds=bed_dicts,
            on_duty_nurses=on_duty_nurse_count,
            nurse_to_patient_ratio=ward.target_nurse_to_patient_ratio
        )

        summaries.append(
            WardCapacitySummary(
                ward_id=ward.id,
                ward_code=ward.code,
                ward_name=ward.name,
                specialty=ward.specialty,
                total_physical_beds=metrics["total_physical_beds"],
                ready_beds=metrics["ready_beds"],
                occupied_beds=metrics["occupied_beds"],
                reserved_beds=metrics["reserved_beds"],
                cleaning_beds=metrics["cleaning_beds"],
                maintenance_beds=metrics["maintenance_beds"],
                blocked_beds=metrics["blocked_beds"],
                on_duty_nurses=metrics["on_duty_nurses"],
                nurse_capacity_ceiling=metrics["nurse_capacity_ceiling"],
                staffed_usable_beds=metrics["staffed_usable_beds"],
                unstaffed_ready_beds=metrics["unstaffed_ready_beds"],
                staffing_deficit=metrics["staffing_deficit"],
                physical_occupancy_rate=metrics["physical_occupancy_rate"],
                staffed_occupancy_rate=metrics["staffed_occupancy_rate"],
            )
        )

    return summaries

