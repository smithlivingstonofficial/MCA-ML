from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.db.session import get_db
from backend.app.db.models import Bed, Ward, HourlyArrivalAggregate, RosterAssignment
from backend.app.domain.bed_lifecycle import BedState
from backend.app.domain.capacity_calculator import calculate_ward_operational_capacity
from backend.app.schemas.hospital import ExecutiveOverviewResponse
from backend.ml.inference.arrival_forecaster import get_arrival_forecaster

router = APIRouter()


@router.get("/overview", response_model=ExecutiveOverviewResponse)
def get_executive_telemetry_overview(db: Session = Depends(get_db)):
    """
    Module 7: Aggregates real-time executive operations telemetry for command-center telemetry.
    """
    # 1. Total Beds & State Counts
    beds = db.query(Bed).all()
    total_physical = len(beds)
    occupied_count = sum(1 for b in beds if b.current_state in [BedState.OCCUPIED.value, BedState.RESERVED.value])
    
    # 2. Ward Capacity Aggregation & Staffing Deficit Alerts
    wards = db.query(Ward).all()
    total_staffed_capacity = 0
    active_alerts = []

    for w in wards:
        w_beds = [b for b in beds if b.ward_id == w.id]
        nurse_count = (
            db.query(RosterAssignment)
            .filter(
                RosterAssignment.ward_id == w.id,
                RosterAssignment.role == "Nurse",
                RosterAssignment.is_on_duty == True
            )
            .count()
        )
        if nurse_count == 0:
            nurse_count = 2

        metrics = calculate_ward_operational_capacity(
            beds=[{"state": b.current_state} for b in w_beds],
            on_duty_nurses=nurse_count,
            nurse_to_patient_ratio=w.target_nurse_to_patient_ratio
        )
        total_staffed_capacity += metrics["nurse_capacity_ceiling"]

        # Alert if staffing deficit exists
        if metrics["staffing_deficit"]:
            active_alerts.append({
                "severity": "WARNING",
                "ward_code": w.code,
                "message": f"Staffing Deficit in {w.name}: {metrics['unstaffed_ready_beds']} ready bed(s) unstaffed.",
                "type": "STAFFING_GAP"
            })

        # Alert if ward occupancy > 85%
        if metrics["staffed_occupancy_rate"] >= 0.85:
            active_alerts.append({
                "severity": "CRITICAL" if metrics["staffed_occupancy_rate"] >= 0.95 else "WARNING",
                "ward_code": w.code,
                "message": f"High Staffed Occupancy in {w.name}: {metrics['staffed_occupancy_rate'] * 100:.1f}%.",
                "type": "CAPACITY_SURGE"
            })

    hospital_occupancy = round(occupied_count / total_physical, 4) if total_physical > 0 else 0.0
    staffed_occupancy = round(occupied_count / total_staffed_capacity, 4) if total_staffed_capacity > 0 else 1.0

    # 3. Emergency Department Arrivals in last 24h
    recent_arrivals = (
        db.query(func.sum(HourlyArrivalAggregate.arrival_count))
        .filter(HourlyArrivalAggregate.department_code == "ED")
        .order_by(HourlyArrivalAggregate.timestamp.desc())
        .limit(24)
        .scalar()
    ) or 0

    # 4. ED Forecast for next 24h
    forecaster = get_arrival_forecaster()
    forecast_points = forecaster.forecast_arrivals(db=db, horizon_hours=24)
    forecast_sum_24h = int(sum(p["predicted_arrivals"] for p in forecast_points))
    overcrowding_flag = any(p["overcrowding_risk"] for p in forecast_points)

    if overcrowding_flag:
        active_alerts.append({
            "severity": "CRITICAL",
            "ward_code": "ED",
            "message": "Emergency Department arrival surge forecast exceeds operational intake capacity in next 24 hours.",
            "type": "ED_OVERCROWDING"
        })

    return ExecutiveOverviewResponse(
        total_census=occupied_count,
        total_physical_beds=total_physical,
        total_staffed_beds=total_staffed_capacity,
        hospital_occupancy_rate=hospital_occupancy,
        staffed_occupancy_rate=staffed_occupancy,
        active_alerts=active_alerts,
        ed_arrivals_last_24h=int(recent_arrivals),
        ed_forecast_next_24h=forecast_sum_24h,
        overcrowding_alert=overcrowding_flag
    )

