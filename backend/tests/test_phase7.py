"""
Module 7 Tests: Phase 7 Real-Time WebSockets, Anomaly Detection & AI Decision Support Copilot.
"""

import pytest
import json
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.broadcaster import broadcaster
from backend.app.domain.anomaly_detector import get_anomaly_detector
from backend.app.domain.copilot_engine import copilot_engine
from backend.app.core.security import create_token, HealthcareRole

client = TestClient(app)


def test_websocket_stream_connection_and_heartbeat():
    """Verify that WebSocket clients connect and receive heartbeats/ping responses."""
    with client.websocket_connect("/ws/live-stream") as websocket:
        # Client sends ping heartbeat
        websocket.send_text("ping")
        data = websocket.receive_text()
        parsed = json.loads(data)
        assert parsed.get("event_type") == "PONG"
        assert "timestamp" in parsed


def test_trigger_stream_event_api():
    """Verify POST /api/v1/stream/trigger-event broadcasts operational alerts into stream."""
    payload = {
        "event_type": "MASS_CASUALTY_INFLOW",
        "module": "Module 1",
        "severity": "CRITICAL",
        "message": "Trauma team activated: 8 acute arrivals inbound within 15 minutes.",
        "payload": {"estimated_esi1_count": 3, "trauma_bays_required": 4}
    }

    res = client.post("/api/v1/stream/trigger-event", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "DISPATCHED"
    assert data["event_type"] == "MASS_CASUALTY_INFLOW"


def test_anomaly_detector_scan():
    """Verify GET /api/v1/anomalies/detect computes multi-vector operational variance."""
    res = client.get("/api/v1/anomalies/detect")
    assert res.status_code == 200
    data = res.json()

    assert "evaluated_at" in data
    assert "anomalies_detected_count" in data
    assert "overall_operational_health_score" in data
    assert 0.0 <= data["overall_operational_health_score"] <= 100.0
    assert "diagnostic_summary" in data
    assert isinstance(data["anomalies"], list)

    for ano in data["anomalies"]:
        assert "anomaly_id" in ano
        assert "category" in ano
        assert ano["severity"] in ["CRITICAL", "WARNING", "INFO"]
        assert "z_score" in ano
        assert "root_cause_analysis" in ano


def test_copilot_recommendations_retrieval():
    """Verify GET /api/v1/copilot/recommendations returns prioritized operational mitigations."""
    res = client.get("/api/v1/copilot/recommendations")
    assert res.status_code == 200
    data = res.json()

    assert data["total_recommendations"] >= 4
    assert "recommendations" in data

    first_rec = data["recommendations"][0]
    assert "recommendation_id" in first_rec
    assert first_rec["urgency"] in ["IMMEDIATE", "HIGH", "MEDIUM"]
    assert "title" in first_rec
    assert "rationalization" in first_rec
    assert "recommended_action" in first_rec
    assert "projected_impact" in first_rec
    assert first_rec["status"] in ["PENDING", "ACKNOWLEDGED", "DISPATCHED"]


def test_copilot_dispatch_action():
    """Verify POST /api/v1/copilot/action/{id}/dispatch executes action and audits event."""
    token = create_token({"sub": "admin", "role": HealthcareRole.HOSPITAL_ADMIN})
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "actor_id": "admin",
        "actor_role": "HOSPITAL_ADMIN",
        "notes": "Authorized emergency float nurse transfer to ICU."
    }

    res = client.post(
        "/api/v1/copilot/action/COPILOT-REC-01/dispatch",
        json=payload,
        headers=headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["recommendation_id"] == "COPILOT-REC-01"
    assert data["status"] == "DISPATCHED"
    assert "dispatched_at" in data

    # Verify recommendation status updated in store
    all_recs = client.get("/api/v1/copilot/recommendations").json()["recommendations"]
    rec1 = next(r for r in all_recs if r["recommendation_id"] == "COPILOT-REC-01")
    assert rec1["status"] == "DISPATCHED"


def test_copilot_dispatch_nonexistent_action_returns_404():
    """Verify dispatching an invalid recommendation returns 404."""
    token = create_token({"sub": "admin", "role": HealthcareRole.HOSPITAL_ADMIN})
    headers = {"Authorization": f"Bearer {token}"}

    res = client.post(
        "/api/v1/copilot/action/NON-EXISTENT-REC-999/dispatch",
        json={"notes": "test"},
        headers=headers
    )
    assert res.status_code == 404
