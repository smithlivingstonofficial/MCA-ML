"""
Module 7: Executive Operational Reports & Data Export Engine.
Provides downloadable CSV cohorts, bed occupancy spreadsheets, and executive briefing summaries.
"""

import io
import csv
from datetime import datetime
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.db.session import get_db
from backend.app.db.models import Bed, Ward, HourlyArrivalAggregate, RosterAssignment, Equipment
from backend.app.schemas.enterprise import ExecutiveBriefResponse
from backend.app.domain.capacity_calculator import calculate_ward_operational_capacity
from backend.app.domain.equipment_tracker import calculate_equipment_and_oxygen_metrics
from backend.ml.inference.arrival_forecaster import get_arrival_forecaster
from backend.ml.governance.drift_monitor import get_governance_engine
from backend.app.api.v1.endpoints.continuity import get_continuity_overview

router = APIRouter()


@router.get("/executive-brief", response_model=ExecutiveBriefResponse)
def get_executive_operational_brief(db: Session = Depends(get_db)):
    """
    Generates a consolidated executive briefing report across all hospital departments.
    """
    beds = db.query(Bed).all()
    total_physical = len(beds)
    occupied = sum(1 for b in beds if b.current_state in ["Occupied", "Reserved"])

    wards = db.query(Ward).all()
    total_staffed = 0
    staffing_deficits = 0

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
        ) or 2

        cap = calculate_ward_operational_capacity(
            beds=[{"state": b.current_state} for b in w_beds],
            on_duty_nurses=nurse_count,
            nurse_to_patient_ratio=w.target_nurse_to_patient_ratio
        )
        total_staffed += cap["nurse_capacity_ceiling"]
        if cap["staffing_deficit"]:
            staffing_deficits += 1

    # Oxygen & Ventilators
    eq_telemetry = calculate_equipment_and_oxygen_metrics(db)
    vent_metrics = eq_telemetry["ventilators"]
    oxy_metrics = eq_telemetry["oxygen_supply"]

    # ED Arrivals & Forecast
    arr_24h = (
        db.query(func.sum(HourlyArrivalAggregate.arrival_count))
        .filter(HourlyArrivalAggregate.department_code == "ED")
        .order_by(HourlyArrivalAggregate.timestamp.desc())
        .limit(24)
        .scalar()
    ) or 0

    forecaster = get_arrival_forecaster()
    forecast_points = forecaster.forecast_arrivals(db=db, horizon_hours=24)
    forecast_24h = int(sum(p["predicted_arrivals"] for p in forecast_points))
    overcrowding = any(p["overcrowding_risk"] for p in forecast_points)

    # Continuity overview
    continuity_ov = get_continuity_overview(limit=50, db=db)

    # Governance
    gov = get_governance_engine()

    return ExecutiveBriefResponse(
        generated_at=datetime.utcnow(),
        hospital_name="Memorial General Hospital - Operations Command Center",
        total_physical_beds=total_physical,
        total_staffed_beds=total_staffed,
        hospital_occupancy_pct=round((occupied / max(total_physical, 1)) * 100, 1),
        staffed_occupancy_pct=round((occupied / max(total_staffed, 1)) * 100, 1),
        ed_arrivals_past_24h=int(arr_24h),
        ed_forecast_next_24h=forecast_24h,
        overcrowding_surge_risk=overcrowding,
        oxygen_days_remaining=oxy_metrics["days_of_supply_remaining"],
        ventilator_utilization_pct=vent_metrics["utilization_pct"],
        critical_staffing_deficits=staffing_deficits,
        high_readmission_risk_cohort_count=continuity_ov.high_risk_count,
        model_governance_status="STABLE",
        active_alerts_count=staffing_deficits + (1 if overcrowding else 0)
    )


@router.get("/readmission-cohort.csv")
def export_readmission_cohort_csv(db: Session = Depends(get_db)):
    """
    Streams a downloadable CSV export of the post-discharge high-risk cohort.
    """
    ov = get_continuity_overview(limit=100, db=db)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Encounter_ID",
        "Patient_MRN",
        "Age",
        "Department",
        "LOS_Hours",
        "Readmission_Risk_Pct",
        "NoShow_Risk_Pct",
        "Risk_Tier",
        "Recommended_Care_Outreach"
    ])

    for p in ov.high_risk_patients:
        writer.writerow([
            p.encounter_id,
            p.patient_mrn,
            p.patient_age,
            p.department,
            p.actual_los_hours,
            f"{p.predicted_readmission_risk * 100:.1f}%",
            f"{(p.predicted_noshow_risk or 0) * 100:.1f}%",
            p.risk_tier,
            p.recommended_outreach
        ])

    output.seek(0)
    filename = f"readmission_risk_cohort_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/bed-occupancy.csv")
def export_bed_occupancy_csv(db: Session = Depends(get_db)):
    """
    Streams a downloadable CSV report of ward bed censuses and staffing status.
    """
    wards = db.query(Ward).all()
    beds = db.query(Bed).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Ward_Code",
        "Ward_Name",
        "Specialty",
        "Total_Physical_Beds",
        "Ready_Beds",
        "Occupied_Beds",
        "Cleaning_Beds",
        "On_Duty_Nurses",
        "Staffed_Capacity_Ceiling",
        "Staffing_Deficit"
    ])

    for w in wards:
        w_beds = [b for b in beds if b.ward_id == w.id]
        ready = sum(1 for b in w_beds if b.current_state == "Ready")
        occupied = sum(1 for b in w_beds if b.current_state in ["Occupied", "Reserved"])
        cleaning = sum(1 for b in w_beds if b.current_state == "Cleaning")

        nurse_count = (
            db.query(RosterAssignment)
            .filter(
                RosterAssignment.ward_id == w.id,
                RosterAssignment.role == "Nurse",
                RosterAssignment.is_on_duty == True
            )
            .count()
        ) or 2

        cap = calculate_ward_operational_capacity(
            beds=[{"state": b.current_state} for b in w_beds],
            on_duty_nurses=nurse_count,
            nurse_to_patient_ratio=w.target_nurse_to_patient_ratio
        )

        writer.writerow([
            w.code,
            w.name,
            w.specialty,
            len(w_beds),
            ready,
            occupied,
            cleaning,
            nurse_count,
            cap["nurse_capacity_ceiling"],
            "YES" if cap["staffing_deficit"] else "NO"
        ])

    output.seek(0)
    filename = f"hospital_bed_occupancy_{datetime.utcnow().strftime('%Y%m%d_%H%M')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
