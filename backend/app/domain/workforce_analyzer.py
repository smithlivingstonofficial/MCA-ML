"""
Module 4: Workforce and clinical staff intelligence engine.
Evaluates doctor and nurse shift coverage, calculates dynamic acuity-driven
staffing deficits, and triggers clinical workload bottleneck warnings.
"""

import math
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from backend.app.db.models import Ward, Bed, RosterAssignment, StaffMember
from backend.app.domain.bed_lifecycle import BedState


def analyze_workforce_deficits(
    db: Session,
    target_date: str = None,
    shift_name: str = "Morning"
) -> Dict[str, Any]:
    """
    Computes required vs. present nursing staff across all wards based on live patient census
    and clinical acuity standards.
    """
    wards = db.query(Ward).all()
    beds = db.query(Bed).all()

    ward_summaries = []
    total_required_nurses = 0
    total_present_nurses = 0
    total_nurse_deficits = 0
    staffing_alerts = []

    for ward in wards:
        # 1. Patient Census in ward (Occupied + Reserved)
        ward_beds = [b for b in beds if b.ward_id == ward.id]
        ward_census = sum(
            1 for b in ward_beds if b.current_state in [BedState.OCCUPIED.value, BedState.RESERVED.value]
        )

        # 2. Nurses present/on-duty in this ward for shift
        roster_query = db.query(RosterAssignment).filter(
            RosterAssignment.ward_id == ward.id,
            RosterAssignment.role == "Nurse",
            RosterAssignment.shift_name == shift_name
        )
        if target_date:
            roster_query = roster_query.filter(RosterAssignment.shift_date == target_date)
            
        roster_assignments = roster_query.all()

        present_nurses = sum(1 for r in roster_assignments if r.status in ["Present", "Scheduled"] and r.is_on_duty)
        # Default minimum safety fallback
        if len(roster_assignments) == 0:
            present_nurses = 2

        # 3. Acuity-driven required nurses
        # ratio: max patients per nurse (e.g., 1.0 for ICU, 3.0 for ED Acute, 4.0 for General)
        ratio = ward.target_nurse_to_patient_ratio
        required_nurses = math.ceil(ward_census / ratio) if ward_census > 0 else 1
        
        deficit = max(0, required_nurses - present_nurses)
        coverage_pct = round((present_nurses / required_nurses) * 100, 1) if required_nurses > 0 else 100.0

        total_required_nurses += required_nurses
        total_present_nurses += present_nurses
        total_nurse_deficits += deficit

        has_deficit = deficit > 0

        if has_deficit:
            staffing_alerts.append({
                "severity": "CRITICAL" if "ICU" in ward.code or deficit >= 2 else "WARNING",
                "ward_code": ward.code,
                "ward_name": ward.name,
                "message": (
                    f"Staff Shortage in {ward.name} ({shift_name} Shift): "
                    f"{deficit} nurse(s) needed. (Present: {present_nurses}, Required: {required_nurses} for {ward_census} patients)."
                ),
                "type": "NURSE_SHORTAGE"
            })

        ward_summaries.append({
            "ward_id": ward.id,
            "ward_code": ward.code,
            "ward_name": ward.name,
            "specialty": ward.specialty,
            "patient_census": ward_census,
            "target_ratio": f"1:{int(ratio)}" if ratio.is_integer() else f"1:{ratio}",
            "required_nurses": required_nurses,
            "present_nurses": present_nurses,
            "nurse_deficit": deficit,
            "coverage_pct": coverage_pct,
            "has_deficit": has_deficit
        })

    hospital_coverage_pct = round(
        (total_present_nurses / total_required_nurses) * 100, 1
    ) if total_required_nurses > 0 else 100.0

    return {
        "shift_name": shift_name,
        "target_date": target_date,
        "hospital_coverage_pct": hospital_coverage_pct,
        "total_required_nurses": total_required_nurses,
        "total_present_nurses": total_present_nurses,
        "total_nurse_deficits": total_nurse_deficits,
        "staffing_alerts": staffing_alerts,
        "ward_summaries": ward_summaries
    }

