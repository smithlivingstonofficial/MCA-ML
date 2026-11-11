from typing import List, Optional
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.db.models import Ward, Bed, Encounter, TriageObservation, RosterAssignment
from backend.app.domain.bed_lifecycle import BedState
from backend.optimization.solvers.bed_allocation_solver import get_bed_allocation_solver
from backend.optimization.scenarios.simulator import (
    simulate_operational_scenario,
    CRISIS_TEMPLATES
)
from backend.app.schemas.optimization import (
    PatientCandidate,
    OptimizationRunResponse,
    SimulationRequest,
    SimulationResponse,
    CrisisTemplateResponse
)

router = APIRouter()


@router.post("/allocate-beds", response_model=OptimizationRunResponse)
def run_bed_allocation_optimization(
    patient_queue: Optional[List[PatientCandidate]] = Body(None),
    db: Session = Depends(get_db)
):
    """
    Module 5: Runs PuLP Mixed-Integer Linear Programming (MILP) solver to optimize
    patient-to-bed allocation under non-negotiable hard clinical safety constraints.
    """
    # 1. Fetch Wards & Nurse Ratios
    wards = db.query(Ward).all()
    ward_dicts = [{"id": w.id, "code": w.code, "name": w.name} for w in wards]

    on_duty_nurses = {}
    nurse_ratios = {}
    existing_census = {}

    for w in wards:
        n_count = (
            db.query(RosterAssignment)
            .filter(
                RosterAssignment.ward_id == w.id,
                RosterAssignment.role == "Nurse",
                RosterAssignment.is_on_duty == True
            )
            .count()
        )
        on_duty_nurses[w.id] = n_count if n_count > 0 else 2
        nurse_ratios[w.id] = w.target_nurse_to_patient_ratio
        
        # Existing census
        occ = (
            db.query(Bed)
            .filter(
                Bed.ward_id == w.id,
                Bed.current_state.in_([BedState.OCCUPIED.value, BedState.RESERVED.value])
            )
            .count()
        )
        existing_census[w.id] = occ

    # 2. Fetch Beds in 'Ready' state
    beds = db.query(Bed).all()
    ward_map = {w.id: w for w in wards}
    bed_dicts = [
        {
            "id": b.id,
            "bed_number": b.bed_number,
            "ward_id": b.ward_id,
            "ward_name": ward_map[b.ward_id].name if b.ward_id in ward_map else "General",
            "specialty": ward_map[b.ward_id].specialty if b.ward_id in ward_map else "General",
            "current_state": b.current_state,
            "is_isolation_capable": b.is_isolation_capable,
            "is_telemetry_capable": b.is_telemetry_capable
        }
        for b in beds
    ]

    # 3. Patient Queue: If not supplied in request, pull recent unadmitted triage encounters
    if patient_queue is None or len(patient_queue) == 0:
        recent_encounters = (
            db.query(Encounter)
            .join(TriageObservation)
            .filter(
                Encounter.encounter_type == "Emergency",
                Encounter.discharge_time == None
            )
            .order_by(TriageObservation.triage_timestamp.desc())
            .limit(10)
            .all()
        )
        patients_to_solve = [
            {
                "id": enc.id,
                "patient_anon_id": enc.patient_anon_id,
                "esi_score": enc.triage.esi_score if enc.triage else 3,
                "chief_complaint": enc.triage.chief_complaint if enc.triage else "Admit",
                "waiting_time_minutes": enc.triage.waiting_time_minutes if enc.triage else 45.0,
                "requires_icu": enc.triage.esi_score in [1, 2] if enc.triage else False,
                "requires_isolation": "Fever" in (enc.triage.chief_complaint if enc.triage else "")
            }
            for enc in recent_encounters
        ]
    else:
        patients_to_solve = [p.model_dump() for p in patient_queue]

    # 4. Execute Solver
    solver = get_bed_allocation_solver()
    result = solver.solve_allocation(
        patients=patients_to_solve,
        beds=bed_dicts,
        wards=ward_dicts,
        on_duty_nurses=on_duty_nurses,
        nurse_ratios=nurse_ratios,
        existing_census=existing_census
    )

    return OptimizationRunResponse(**result)


@router.post("/simulate-scenario", response_model=SimulationResponse)
def run_scenario_simulation(
    payload: SimulationRequest,
    db: Session = Depends(get_db)
):
    """
    Module 5: Executes what-if operational surge simulation comparing baseline vs crisis metrics.
    """
    result = simulate_operational_scenario(
        db=db,
        arrival_surge_multiplier=payload.arrival_surge_multiplier,
        nurse_absenteeism_pct=payload.nurse_absenteeism_pct,
        out_of_service_bed_pct=payload.out_of_service_bed_pct,
        simulation_horizon_hours=payload.horizon_hours
    )
    return SimulationResponse(**result)


@router.get("/crisis-templates", response_model=List[CrisisTemplateResponse])
def get_crisis_templates():
    """
    Module 5: Returns standardized disaster and surge scenarios for one-click simulation.
    """
    return [
        CrisisTemplateResponse(template_key=k, **v)
        for k, v in CRISIS_TEMPLATES.items()
    ]

