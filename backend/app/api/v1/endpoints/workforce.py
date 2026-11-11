from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.db.models import RosterAssignment, Ward
from backend.app.domain.workforce_analyzer import analyze_workforce_deficits
from backend.app.schemas.resource import (
    WorkforceDeficitResponse,
    RosterAssignmentResponse,
    StatusUpdateRequest
)

router = APIRouter()


@router.get("/deficits", response_model=WorkforceDeficitResponse)
def get_workforce_deficits(
    shift: str = Query("Morning", description="Shift name: Morning, Evening, or Night"),
    date_str: Optional[str] = Query(None, description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db)
):
    """
    Module 4: Computes dynamic acuity-driven nurse-to-patient staffing deficits
    and triggers departmental shortage alerts.
    """
    if not date_str:
        date_str = date.today().strftime("%Y-%m-%d")

    data = analyze_workforce_deficits(db=db, target_date=date_str, shift_name=shift)
    return WorkforceDeficitResponse(**data)


@router.get("/roster", response_model=List[RosterAssignmentResponse])
def get_roster_schedule(
    ward_id: Optional[str] = None,
    shift: Optional[str] = None,
    date_str: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Module 4: Retrieves staff shift assignments with attendance status.
    """
    query = db.query(RosterAssignment)
    if ward_id:
        query = query.filter(RosterAssignment.ward_id == ward_id)
    if shift:
        query = query.filter(RosterAssignment.shift_name == shift)
    if date_str:
        query = query.filter(RosterAssignment.shift_date == date_str)

    return query.order_by(RosterAssignment.shift_date.desc(), RosterAssignment.shift_name).all()


@router.patch("/assignments/{assignment_id}/status", response_model=RosterAssignmentResponse)
def update_assignment_status(
    assignment_id: str,
    payload: StatusUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Module 4: Updates staff member shift attendance (Scheduled, Present, Absent, OnCall).
    """
    assignment = db.query(RosterAssignment).filter(RosterAssignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Roster assignment '{assignment_id}' not found."
        )

    valid_statuses = ["Scheduled", "Present", "Absent", "OnCall"]
    if payload.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid status '{payload.status}'. Must be one of: {valid_statuses}"
        )

    assignment.status = payload.status
    if payload.is_on_duty is not None:
        assignment.is_on_duty = payload.is_on_duty
    else:
        assignment.is_on_duty = payload.status in ["Present", "Scheduled"]

    db.commit()
    db.refresh(assignment)
    return assignment
