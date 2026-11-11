import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.domain.bed_lifecycle import (
    BedState, validate_bed_transition, InvalidBedStateTransitionError
)
from backend.app.domain.capacity_calculator import calculate_ward_operational_capacity


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_bed_state_machine_valid_transitions():
    # Ready -> Reserved -> Occupied -> Cleaning -> Ready
    assert validate_bed_transition(BedState.READY, BedState.RESERVED) is True
    assert validate_bed_transition(BedState.RESERVED, BedState.OCCUPIED) is True
    assert validate_bed_transition(BedState.OCCUPIED, BedState.CLEANING) is True
    assert validate_bed_transition(BedState.CLEANING, BedState.READY) is True


def test_bed_state_machine_invalid_transitions():
    # Direct transition from Cleaning to Occupied without Ready is illegal
    with pytest.raises(InvalidBedStateTransitionError):
        validate_bed_transition(BedState.CLEANING, BedState.OCCUPIED)

    # Direct transition from Maintenance to Occupied is illegal
    with pytest.raises(InvalidBedStateTransitionError):
        validate_bed_transition(BedState.MAINTENANCE, BedState.OCCUPIED)


def test_operational_capacity_calculator():
    # 10 physical beds: 4 Ready, 4 Occupied, 2 Cleaning
    # On duty nurses = 1, ratio = 4.0 -> Nurse ceiling = 4 patients
    # Current census = 4 occupied -> Available nurse capacity = 0 -> Staffed usable beds = 0
    beds = [
        {"state": BedState.READY.value},
        {"state": BedState.READY.value},
        {"state": BedState.READY.value},
        {"state": BedState.READY.value},
        {"state": BedState.OCCUPIED.value},
        {"state": BedState.OCCUPIED.value},
        {"state": BedState.OCCUPIED.value},
        {"state": BedState.OCCUPIED.value},
        {"state": BedState.CLEANING.value},
        {"state": BedState.CLEANING.value},
    ]

    metrics = calculate_ward_operational_capacity(
        beds=beds,
        on_duty_nurses=1,
        nurse_to_patient_ratio=4.0
    )

    assert metrics["total_physical_beds"] == 10
    assert metrics["ready_beds"] == 4
    assert metrics["nurse_capacity_ceiling"] == 4
    assert metrics["staffed_usable_beds"] == 0
    assert metrics["staffing_deficit"] is True
    assert metrics["unstaffed_ready_beds"] == 4


def test_api_list_beds():
    response = client.get("/api/v1/beds")
    assert response.status_code == 200
    beds = response.json()
    assert len(beds) > 0
    assert "bed_number" in beds[0]
    assert "current_state" in beds[0]


def test_api_operational_capacity():
    response = client.get("/api/v1/beds/capacity")
    assert response.status_code == 200
    wards = response.json()
    assert len(wards) == 8
    for w in wards:
        assert "staffed_usable_beds" in w
        assert "total_physical_beds" in w


def test_api_arrival_forecast():
    response = client.get("/api/v1/arrivals/forecast?horizon=24")
    assert response.status_code == 200
    data = response.json()
    assert data["horizon_hours"] == 24
    assert len(data["forecasts"]) == 24
    first_pt = data["forecasts"][0]
    assert "predicted_arrivals" in first_pt
    assert "lower_bound_80" in first_pt
    assert "upper_bound_80" in first_pt
    assert first_pt["lower_bound_80"] <= first_pt["predicted_arrivals"] <= first_pt["upper_bound_80"]


def test_api_executive_telemetry():
    response = client.get("/api/v1/telemetry/overview")
    assert response.status_code == 200
    overview = response.json()
    assert overview["total_physical_beds"] == 120
    assert "hospital_occupancy_rate" in overview
    assert "staffed_occupancy_rate" in overview
    assert "active_alerts" in overview


def test_api_illegal_bed_transition_returns_422():
    # Find a bed currently in Cleaning or change one to Cleaning
    response = client.get("/api/v1/beds")
    beds = response.json()
    bed_id = beds[0]["id"]
    
    # Try invalid transition from current state to an illegal state
    current_st = beds[0]["current_state"]
    illegal_target = "Occupied" if current_st == "Cleaning" else "Cleaning"
    if current_st != "Occupied":
        # Trying to transition a non-occupied bed directly to Cleaning violates the state machine
        patch_res = client.patch(
            f"/api/v1/beds/{bed_id}/state",
            json={"new_state": "Cleaning", "reason": "Test illegal transition"}
        )
        assert patch_res.status_code == 422

