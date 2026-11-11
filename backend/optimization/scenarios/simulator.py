"""
Module 5: What-If Scenario Simulator for emergency surges and operational crisis modeling.
Simulates parameter perturbations (arrival surges, staff absenteeism, bed maintenance holds)
and provides side-by-side comparative operational impact analyses.
"""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.db.models import Ward, Bed, HourlyArrivalAggregate, RosterAssignment
from backend.app.domain.bed_lifecycle import BedState
from backend.app.domain.capacity_calculator import calculate_ward_operational_capacity


CRISIS_TEMPLATES = {
    "FLU_EPIDEMIC": {
        "name": "Flu Epidemic Surge",
        "description": "Seasonal respiratory infection wave (+40% arrivals, 15% nurse absenteeism)",
        "arrival_surge_multiplier": 1.40,
        "nurse_absenteeism_pct": 0.15,
        "out_of_service_bed_pct": 0.05
    },
    "MASS_CASUALTY": {
        "name": "Mass Casualty Incident",
        "description": "Multi-vehicle highway pileup (+80% arrivals, high ICU/trauma demand)",
        "arrival_surge_multiplier": 1.80,
        "nurse_absenteeism_pct": 0.00,
        "out_of_service_bed_pct": 0.10
    },
    "BLIZZARD_TRANSIT_OUTAGE": {
        "name": "Severe Blizzard / Transit Strike",
        "description": "Severe weather hindering staff transit (35% nurse absenteeism, nominal arrivals)",
        "arrival_surge_multiplier": 1.05,
        "nurse_absenteeism_pct": 0.35,
        "out_of_service_bed_pct": 0.05
    }
}


def simulate_operational_scenario(
    db: Session,
    arrival_surge_multiplier: float = 1.0,
    nurse_absenteeism_pct: float = 0.0,
    out_of_service_bed_pct: float = 0.0,
    simulation_horizon_hours: int = 24
) -> Dict[str, Any]:
    """
    Executes what-if simulation comparing baseline operational capacity against simulated crisis parameters.
    """
    # 1. Fetch current baseline facts
    wards = db.query(Ward).all()
    all_beds = db.query(Bed).all()
    
    # 24h baseline arrivals
    baseline_arrivals = (
        db.query(func.sum(HourlyArrivalAggregate.arrival_count))
        .filter(HourlyArrivalAggregate.department_code == "ED")
        .order_by(HourlyArrivalAggregate.timestamp.desc())
        .limit(simulation_horizon_hours)
        .scalar()
    ) or (7.5 * simulation_horizon_hours)

    simulated_arrivals = int(baseline_arrivals * arrival_surge_multiplier)

    # 2. Compute Baseline vs Simulated Capacity per Ward
    baseline_wards_metrics = []
    simulated_wards_metrics = []

    total_baseline_staffed = 0
    total_simulated_staffed = 0

    total_baseline_ready = 0
    total_simulated_ready = 0

    total_census = sum(1 for b in all_beds if b.current_state in [BedState.OCCUPIED.value, BedState.RESERVED.value])

    actionable_recommendations = []

    for ward in wards:
        ward_beds = [b for b in all_beds if b.ward_id == ward.id]
        
        # Baseline nurse count
        base_nurses = (
            db.query(RosterAssignment)
            .filter(
                RosterAssignment.ward_id == ward.id,
                RosterAssignment.role == "Nurse",
                RosterAssignment.is_on_duty == True
            )
            .count()
        )
        if base_nurses == 0:
            base_nurses = 2

        # Baseline calculations
        base_calc = calculate_ward_operational_capacity(
            beds=[{"state": b.current_state} for b in ward_beds],
            on_duty_nurses=base_nurses,
            nurse_to_patient_ratio=ward.target_nurse_to_patient_ratio
        )
        total_baseline_staffed += base_calc["nurse_capacity_ceiling"]
        total_baseline_ready += base_calc["ready_beds"]
        baseline_wards_metrics.append({
            "ward_code": ward.code,
            "ward_name": ward.name,
            "staffed_usable": base_calc["staffed_usable_beds"],
            "occupancy_rate": base_calc["staffed_occupancy_rate"]
        })

        # --- SIMULATED CRISIS ADJUSTMENTS ---
        # 1. Nurse reduction due to absenteeism
        sim_nurses = max(1, int(round(base_nurses * (1.0 - nurse_absenteeism_pct))))
        
        # 2. Bed reduction due to out-of-service/blocked
        sim_beds = []
        for b in ward_beds:
            state = b.current_state
            # Some fraction of ready beds becomes blocked
            if state == BedState.READY.value and out_of_service_bed_pct > 0:
                import random
                if random.random() < out_of_service_bed_pct:
                    state = BedState.BLOCKED.value
            sim_beds.append({"state": state})

        sim_calc = calculate_ward_operational_capacity(
            beds=sim_beds,
            on_duty_nurses=sim_nurses,
            nurse_to_patient_ratio=ward.target_nurse_to_patient_ratio
        )
        total_simulated_staffed += sim_calc["nurse_capacity_ceiling"]
        total_simulated_ready += sim_calc["ready_beds"]

        simulated_wards_metrics.append({
            "ward_code": ward.code,
            "ward_name": ward.name,
            "staffed_usable": sim_calc["staffed_usable_beds"],
            "occupancy_rate": sim_calc["staffed_occupancy_rate"],
            "deficit": sim_calc["staffing_deficit"]
        })

        # Specific recommendations
        if sim_calc["staffing_deficit"]:
            actionable_recommendations.append(
                f"Ward {ward.name}: Deploy {sim_calc['unstaffed_ready_beds']} float-pool nurse(s) to unlock {sim_calc['unstaffed_ready_beds']} offline bed(s)."
            )

    # Global KPI Comparison
    baseline_occupancy = round(total_census / total_baseline_staffed, 4) if total_baseline_staffed > 0 else 1.0
    simulated_occupancy = round((total_census + (simulated_arrivals - baseline_arrivals) * 0.35) / total_simulated_staffed, 4) if total_simulated_staffed > 0 else 1.5

    # Hospital Stress Index (0-100%)
    stress_index = min(100.0, round(simulated_occupancy * 100.0 * (1.0 + (simulated_arrivals / baseline_arrivals - 1.0) * 0.3), 1))

    if simulated_occupancy > 1.0:
        over_pts = int((simulated_occupancy - 1.0) * total_simulated_staffed)
        actionable_recommendations.insert(0, f"Critical Surge: {over_pts} incoming patients cannot be accommodated under current staffing. Activate regional diversion protocol.")

    return {
        "parameters": {
            "arrival_surge_multiplier": arrival_surge_multiplier,
            "nurse_absenteeism_pct": nurse_absenteeism_pct,
            "out_of_service_bed_pct": out_of_service_bed_pct,
            "horizon_hours": simulation_horizon_hours
        },
        "baseline": {
            "arrivals_24h": int(baseline_arrivals),
            "total_staffed_capacity": total_baseline_staffed,
            "ready_beds": total_baseline_ready,
            "staffed_occupancy_pct": round(baseline_occupancy * 100, 1),
            "ward_breakdown": baseline_wards_metrics
        },
        "simulated": {
            "arrivals_24h": simulated_arrivals,
            "total_staffed_capacity": total_simulated_staffed,
            "ready_beds": total_simulated_ready,
            "staffed_occupancy_pct": round(simulated_occupancy * 100, 1),
            "hospital_stress_index": stress_index,
            "is_critical_overcapacity": simulated_occupancy > 1.0,
            "ward_breakdown": simulated_wards_metrics
        },
        "recommendations": actionable_recommendations
    }

