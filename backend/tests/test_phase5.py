"""
Module 7 Tests: Model Governance, Population Stability Index (PSI), KS Drift & Data Quality.
"""

import pytest
import numpy as np
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.ml.governance.drift_monitor import calculate_psi, calculate_ks_drift, get_governance_engine

client = TestClient(app)


def test_psi_calculation_identical_distributions():
    """Verify that identical baseline and target distributions produce PSI near 0 (STABLE)."""
    rng = np.random.default_rng(42)
    baseline = rng.normal(loc=20.0, scale=4.0, size=1000)
    target = rng.normal(loc=20.0, scale=4.0, size=1000)

    psi, status, buckets = calculate_psi(baseline, target, num_buckets=10)

    assert psi < 0.10
    assert status == "STABLE"
    assert len(buckets) == 10


def test_psi_calculation_drifted_distribution():
    """Verify that a substantial distribution shift triggers CRITICAL_DRIFT (PSI >= 0.25)."""
    rng = np.random.default_rng(42)
    baseline = rng.normal(loc=20.0, scale=3.0, size=1000)
    target = rng.normal(loc=35.0, scale=3.0, size=1000)  # Major surge shift

    psi, status, _ = calculate_psi(baseline, target, num_buckets=10)

    assert psi >= 0.25
    assert status == "CRITICAL_DRIFT"


def test_ks_drift_detection():
    """Verify that Kolmogorov-Smirnov test flags distribution divergence."""
    rng = np.random.default_rng(42)
    baseline = rng.exponential(scale=10.0, size=500)
    target_shifted = rng.exponential(scale=25.0, size=500)
    target_stable = rng.exponential(scale=10.0, size=500)

    res_shifted = calculate_ks_drift(baseline, target_shifted)
    assert res_shifted["drift_detected"] is True
    assert res_shifted["p_value"] < 0.05

    res_stable = calculate_ks_drift(baseline, target_stable)
    assert res_stable["drift_detected"] is False
    assert res_stable["p_value"] >= 0.05


def test_data_quality_validator():
    """Verify healthcare data quality integrity checks on timestamps and value bounds."""
    gov_engine = get_governance_engine()

    encounters = [
        {"encounter_type": "Emergency", "arrival_time": "2026-11-11T10:00:00", "esi_score": 2, "actual_los_hours": 36.0},
        {"encounter_type": "Inpatient", "arrival_time": "2026-11-11T11:00:00", "esi_score": 3, "actual_los_hours": 72.0},
        {"encounter_type": "Emergency", "arrival_time": "2026-11-11T12:00:00", "esi_score": 7, "actual_los_hours": -5.0}, # 2 range anomalies
    ]

    report = gov_engine.validate_data_quality(encounters)

    assert report["records_audited"] == 3
    assert report["range_anomalies"] >= 1
    assert report["quality_score_pct"] < 100.0


def test_api_governance_telemetry():
    """Verify GET /api/v1/telemetry/governance returns full drift and model registry telemetry."""
    response = client.get("/api/v1/telemetry/governance")
    assert response.status_code == 200
    data = response.json()

    assert "overall_governance_status" in data
    assert "active_models" in data
    assert len(data["active_models"]) >= 3
    assert "features" in data
    assert "hourly_arrivals" in data["features"]
    assert "length_of_stay" in data["features"]
    assert "triage_acuity_esi" in data["features"]
    assert "data_quality" in data
    assert data["data_quality"]["records_audited"] > 0
    assert "recommendation" in data
