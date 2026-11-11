import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.optimization.solvers.bed_allocation_solver import BedAllocationSolver


client = TestClient(app)


def test_pulp_solver_basic_feasibility():
    """Verify that PuLP allocates patients to ready beds under normal capacity."""
    solver = BedAllocationSolver()

    patients = [
        {"id": "P1", "patient_anon_id": "PAT-001", "esi_score": 3, "requires_icu": False, "requires_isolation": False, "waiting_time_minutes": 30.0},
        {"id": "P2", "patient_anon_id": "PAT-002", "esi_score": 4, "requires_icu": False, "requires_isolation": False, "waiting_time_minutes": 15.0},
    ]

    beds = [
        {"id": "B1", "bed_number": "MED-01", "ward_id": "W_MED", "ward_name": "General Med", "specialty": "General", "current_state": "Ready", "is_isolation_capable": False},
        {"id": "B2", "bed_number": "MED-02", "ward_id": "W_MED", "ward_name": "General Med", "specialty": "General", "current_state": "Ready", "is_isolation_capable": False},
    ]

    wards = [{"id": "W_MED", "code": "MED", "name": "General Med"}]
    on_duty_nurses = {"W_MED": 2}
    nurse_ratios = {"W_MED": 4.0}
    existing_census = {"W_MED": 2}

    result = solver.solve_allocation(
        patients=patients,
        beds=beds,
        wards=wards,
        on_duty_nurses=on_duty_nurses,
        nurse_ratios=nurse_ratios,
        existing_census=existing_census
    )

    assert result["status"] == "Optimal"
    assert result["assigned_count"] == 2
    assert result["unassigned_count"] == 0
    assert len(result["assignments"]) == 2


def test_pulp_hard_constraint_icu_matching():
    """Verify that an ICU patient (ESI 1) can NEVER be allocated to a General ward bed."""
    solver = BedAllocationSolver()

    # Patient requires ICU
    patients = [
        {"id": "P_CRITICAL", "patient_anon_id": "PAT-CRIT", "esi_score": 1, "requires_icu": True, "requires_isolation": False}
    ]

    # Only a General Medicine bed is ready; ICU bed is Cleaning
    beds = [
        {"id": "B_GEN", "bed_number": "MED-01", "ward_id": "W_MED", "specialty": "General", "current_state": "Ready", "is_isolation_capable": False},
        {"id": "B_ICU", "bed_number": "ICU-01", "ward_id": "W_ICU", "specialty": "ICU", "current_state": "Cleaning", "is_isolation_capable": True},
    ]

    wards = [
        {"id": "W_MED", "code": "MED", "name": "General Med"},
        {"id": "W_ICU", "code": "ICU", "name": "ICU North"},
    ]
    on_duty_nurses = {"W_MED": 2, "W_ICU": 2}
    nurse_ratios = {"W_MED": 4.0, "W_ICU": 1.0}
    existing_census = {"W_MED": 0, "W_ICU": 0}

    result = solver.solve_allocation(
        patients=patients,
        beds=beds,
        wards=wards,
        on_duty_nurses=on_duty_nurses,
        nurse_ratios=nurse_ratios,
        existing_census=existing_census
    )

    # Must NOT assign ICU patient to General bed
    assert result["assigned_count"] == 0
    assert result["unassigned_count"] == 1
    assert "Insufficient staffed ICU bed capacity" in result["diagnostics"][0]


def test_pulp_hard_constraint_isolation():
    """Verify that a patient requiring isolation is ONLY assigned to an isolation-capable bed."""
    solver = BedAllocationSolver()

    patients = [
        {"id": "P_ISO", "patient_anon_id": "PAT-ISO", "esi_score": 3, "requires_icu": False, "requires_isolation": True}
    ]

    # Bed 1 is regular; Bed 2 is isolation capable
    beds = [
        {"id": "B_REG", "bed_number": "MED-01", "ward_id": "W_MED", "specialty": "General", "current_state": "Ready", "is_isolation_capable": False},
        {"id": "B_ISO", "bed_number": "MED-02", "ward_id": "W_MED", "specialty": "General", "current_state": "Ready", "is_isolation_capable": True},
    ]

    wards = [{"id": "W_MED", "code": "MED", "name": "General Med"}]
    on_duty_nurses = {"W_MED": 2}
    nurse_ratios = {"W_MED": 4.0}
    existing_census = {"W_MED": 0}

    result = solver.solve_allocation(
        patients=patients,
        beds=beds,
        wards=wards,
        on_duty_nurses=on_duty_nurses,
        nurse_ratios=nurse_ratios,
        existing_census=existing_census
    )

    assert result["assigned_count"] == 1
    assigned = result["assignments"][0]
    assert assigned["bed_id"] == "B_ISO"
    assert assigned["is_isolation_certified"] is True


def test_api_allocate_beds():
    response = client.post("/api/v1/optimization/allocate-beds", json=[])
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "total_patients" in data
    assert "execution_time_ms" in data


def test_api_simulate_scenario():
    response = client.post(
        "/api/v1/optimization/simulate-scenario",
        json={
            "arrival_surge_multiplier": 1.4,
            "nurse_absenteeism_pct": 0.15,
            "out_of_service_bed_pct": 0.05,
            "horizon_hours": 24
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "baseline" in data
    assert "simulated" in data
    assert data["simulated"]["arrivals_24h"] > data["baseline"]["arrivals_24h"]
    assert "hospital_stress_index" in data["simulated"]
    assert len(data["recommendations"]) > 0


def test_api_crisis_templates():
    response = client.get("/api/v1/optimization/crisis-templates")
    assert response.status_code == 200
    templates = response.json()
    assert len(templates) >= 3
    keys = [t["template_key"] for t in templates]
    assert "FLU_EPIDEMIC" in keys
    assert "MASS_CASUALTY" in keys

