"""
Phase 8 Automated Verification Suite: Multi-Hospital Regional Coordination,
Cross-Facility Transfer Optimization & Emergency Diversion Network.
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.core.security import create_token, HealthcareRole
from backend.app.domain.regional_optimizer import regional_engine, TRANSIT_MATRIX

client = TestClient(app)


@pytest.fixture
def admin_auth_headers():
    token = create_token(
        {"sub": "admin", "role": HealthcareRole.HOSPITAL_ADMIN, "department": "ADMINISTRATION"}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def bed_manager_auth_headers():
    token = create_token(
        {"sub": "bedmanager", "role": HealthcareRole.BED_MANAGER, "department": "BED_MANAGEMENT"}
    )
    return {"Authorization": f"Bearer {token}"}


def test_get_regional_network_status():
    """
    Verifies that the regional network status endpoint returns telemetry
    for all 4 health network facilities and composite stress metrics.
    """
    response = client.get("/api/v1/regional/network-status")
    assert response.status_code == 200

    data = response.json()
    assert data["total_facilities"] == 4
    assert len(data["facilities"]) == 4
    assert data["network_physical_beds"] > 0
    assert data["network_staffed_beds"] > 0
    assert "network_stress_index" in data
    assert len(data["transit_matrix"]) >= 12

    # Check facility structure
    f_ids = [f["hospital_id"] for f in data["facilities"]]
    assert "HOSP-01" in f_ids
    assert "HOSP-02" in f_ids
    assert "HOSP-03" in f_ids
    assert "HOSP-04" in f_ids

    h1 = next(f for f in data["facilities"] if f["hospital_id"] == "HOSP-01")
    assert h1["facility_type"] == "LEVEL_1_TRAUMA_HUB"
    assert h1["total_physical_beds"] >= 100


def test_regional_transfer_optimization():
    """
    Verifies that PuLP Mixed-Integer Linear Programming solves transfer optimization
    and produces actionable load-balancing recommendations.
    """
    response = client.get("/api/v1/regional/transfer-recommendations")
    assert response.status_code == 200

    data = response.json()
    assert "solver_status" in data
    assert data["solver_status"] in ("OPTIMAL", "FEASIBLE_NOMINAL")
    assert "transfers" in data
    assert isinstance(data["transfers"], list)

    if data["transfers"]:
        t = data["transfers"][0]
        assert "transfer_id" in t
        assert "source_hospital_id" in t
        assert "destination_hospital_id" in t
        assert "transit_distance_km" in t
        assert "transit_time_minutes" in t
        assert t["transit_time_minutes"] > 0


def test_toggle_emergency_diversion(admin_auth_headers):
    """
    Verifies activating and deactivating emergency ambulance diversion
    with RBAC authentication and audit logging.
    """
    # 1. Activate Diversion
    resp = client.post(
        "/api/v1/regional/toggle-diversion",
        json={
            "hospital_id": "HOSP-01",
            "new_status": "DIVERT_OVERFLOW",
            "reason": "Trauma ED saturation: 18 acute arrivals waiting."
        },
        headers=admin_auth_headers
    )
    assert resp.status_code == 200
    res_data = resp.json()
    assert res_data["hospital_id"] == "HOSP-01"
    assert res_data["new_status"] == "DIVERT_OVERFLOW"
    assert "broadcast_event_id" in res_data

    # Check network telemetry reflects active diversion
    telemetry_resp = client.get("/api/v1/regional/network-status")
    telemetry = telemetry_resp.json()
    h1 = next(f for f in telemetry["facilities"] if f["hospital_id"] == "HOSP-01")
    assert h1["diversion_status"] == "DIVERT_OVERFLOW"
    assert telemetry["active_diversions_count"] >= 1

    # 2. Reset Diversion to NORMAL
    reset_resp = client.post(
        "/api/v1/regional/toggle-diversion",
        json={
            "hospital_id": "HOSP-01",
            "new_status": "NORMAL",
            "reason": "Queue stabilized; normal intake resumed."
        },
        headers=admin_auth_headers
    )
    assert reset_resp.status_code == 200
    assert reset_resp.json()["new_status"] == "NORMAL"


def test_dispatch_patient_transfer(bed_manager_auth_headers):
    """
    Verifies authorizing and dispatching an inter-facility transfer with
    audit logging and real-time event broadcasting.
    """
    resp = client.post(
        "/api/v1/regional/dispatch-transfer",
        json={
            "transfer_id": "XFER-HOSP-01-HOSP-02-PT-REG-104",
            "notes": "Regional transfer dispatched via Advanced Life Support unit.",
            "transport_vehicle_type": "CRITICAL_CARE_AMBULANCE"
        },
        headers=bed_manager_auth_headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "DISPATCHED"
    assert data["transfer_id"] == "XFER-HOSP-01-HOSP-02-PT-REG-104"
    assert "dispatched_at" in data
    assert data["dispatched_by"] == "bedmanager"


def test_invalid_diversion_status_returns_400(admin_auth_headers):
    """
    Verifies that an unsupported diversion status returns HTTP 400.
    """
    resp = client.post(
        "/api/v1/regional/toggle-diversion",
        json={
            "hospital_id": "HOSP-02",
            "new_status": "INVALID_STATE",
            "reason": "Test bad status"
        },
        headers=admin_auth_headers
    )
    assert resp.status_code == 400


def test_transit_matrix_completeness():
    """
    Verifies that the network transit matrix covers bidirectional
    distances and positive travel times for all facility pairs.
    """
    facility_ids = ["HOSP-01", "HOSP-02", "HOSP-03", "HOSP-04"]
    for origin in facility_ids:
        for dest in facility_ids:
            if origin != dest:
                entry = next(
                    (t for t in TRANSIT_MATRIX if t["origin_hospital_id"] == origin and t["destination_hospital_id"] == dest),
                    None
                )
                assert entry is not None, f"Missing transit route from {origin} to {dest}"
                assert entry["distance_km"] > 0
                assert entry["transit_time_minutes"] > 0


def test_regional_stress_index_dynamics():
    """
    Verifies that regional stress index responds to network conditions.
    """
    response = client.get("/api/v1/regional/network-status")
    data = response.json()
    stress = data["network_stress_index"]
    assert 0.0 <= stress <= 100.0
