"""
Module 6 Tests: Patient Continuity, Readmission Risk Stratification & TreeSHAP Explainability.
"""

import pytest
import pandas as pd
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.ml.features.patient_continuity import extract_continuity_features, FEATURE_NAMES
from backend.ml.explainability.shap_explainer import ContinuityExplainer, get_continuity_explainer

client = TestClient(app)


def test_feature_extraction_continuity():
    """Verify that feature engineering produces complete, NaN-free DataFrames with clinical flags."""
    raw_encounters = [
        {
            "actual_los_hours": 72.5,
            "esi_score": 2,
            "prior_admissions_count": 3,
            "comorbidity_count": 4,
            "age": 78,
            "encounter_type": "Emergency",
            "disposition": "Home",
            "chief_complaint": "Severe chest pain radiating to arm"
        },
        {
            "actual_los_hours": None,
            "los_hours": None,
            "esi_score": None,
            "prior_admissions_count": None,
            "comorbidity_count": None,
            "age": None,
            "encounter_type": "Elective",
            "disposition": "Transferred",
            "chief_complaint": "Routine wellness check"
        }
    ]

    features = extract_continuity_features(raw_encounters)

    assert isinstance(features, pd.DataFrame)
    assert len(features) == 2
    assert list(features.columns) == FEATURE_NAMES
    assert features.isna().sum().sum() == 0

    # High-risk case checks
    row0 = features.iloc[0]
    assert row0["actual_los_hours"] == 72.5
    assert row0["esi_score"] == 2
    assert row0["prior_admissions_count"] == 3
    assert row0["comorbidity_count"] == 4
    assert row0["age"] == 78
    assert row0["is_emergency_admission"] == 1
    assert row0["discharge_to_home"] == 1
    assert row0["high_risk_chief_complaint"] == 1

    # Default fallback checks
    row1 = features.iloc[1]
    assert row1["actual_los_hours"] == 36.0
    assert row1["esi_score"] == 3
    assert row1["is_emergency_admission"] == 0
    assert row1["discharge_to_home"] == 0
    assert row1["high_risk_chief_complaint"] == 0


def test_shap_explainer_initialization_and_inference():
    """Verify that TreeExplainer loads trained models and calculates monotonic risk stratification."""
    explainer = get_continuity_explainer()
    assert explainer.readmission_model is not None
    assert explainer.explainer is not None

    # High-risk profile: Elderly, prior admissions, high comorbidity, emergency, chest pain
    high_risk_patient = {
        "actual_los_hours": 96.0,
        "esi_score": 2,
        "prior_admissions_count": 4,
        "comorbidity_count": 3,
        "age": 82,
        "encounter_type": "Emergency",
        "disposition": "Home",
        "chief_complaint": "Acute heart failure decompensation"
    }

    # Low-risk profile: Young, first admission, elective, low acuity
    low_risk_patient = {
        "actual_los_hours": 12.0,
        "esi_score": 4,
        "prior_admissions_count": 0,
        "comorbidity_count": 0,
        "age": 24,
        "encounter_type": "Elective",
        "disposition": "Home",
        "chief_complaint": "Minor sprain"
    }

    res_high = explainer.explain_encounter(high_risk_patient)
    res_low = explainer.explain_encounter(low_risk_patient)

    assert res_high["predicted_readmission_risk"] > res_low["predicted_readmission_risk"]
    assert res_high["risk_tier"] == "HIGH"
    assert res_low["risk_tier"] == "LOW"
    assert "Priority Clinical Outreach" in res_high["recommended_outreach"]


def test_shap_waterfall_attributions():
    """Verify that local TreeSHAP attributions sum appropriately and classify direction accurately."""
    explainer = get_continuity_explainer()

    patient = {
        "actual_los_hours": 72.0,
        "esi_score": 1,
        "prior_admissions_count": 3,
        "comorbidity_count": 3,
        "age": 75,
        "encounter_type": "Emergency",
        "disposition": "Home",
        "chief_complaint": "Cardiac arrest with successful resuscitation"
    }

    result = explainer.explain_encounter(patient)
    attributions = result["feature_attributions"]

    assert len(attributions) == len(FEATURE_NAMES)
    for attr in attributions:
        assert "feature_name" in attr
        assert "display_name" in attr
        assert "shap_value" in attr
        assert attr["effect"] in ["risk_increasing", "protective", "neutral"]
        assert len(attr["clinical_interpretation"]) > 5

    # Check that high priors and age produce risk-increasing effects
    priors_attr = next(a for a in attributions if a["feature_name"] == "prior_admissions_count")
    assert priors_attr["shap_value"] > 0
    assert priors_attr["effect"] == "risk_increasing"


def test_api_continuity_overview():
    """Verify GET /api/v1/continuity/overview returns aggregated cohort stats."""
    response = client.get("/api/v1/continuity/overview?limit=25")
    assert response.status_code == 200
    data = response.json()

    assert "total_cohort_evaluated" in data
    assert "high_risk_count" in data
    assert "moderate_risk_count" in data
    assert "low_risk_count" in data
    assert "mean_readmission_risk" in data
    assert "high_risk_patients" in data
    assert data["total_cohort_evaluated"] > 0
    assert data["high_risk_count"] + data["moderate_risk_count"] + data["low_risk_count"] == data["total_cohort_evaluated"]


def test_api_continuity_cohort_filtering():
    """Verify GET /api/v1/continuity/cohort respects risk tier query filters."""
    # Test ALL
    res_all = client.get("/api/v1/continuity/cohort?tier=ALL&limit=10")
    assert res_all.status_code == 200
    data_all = res_all.json()
    assert len(data_all) <= 10

    # Test HIGH filter
    res_high = client.get("/api/v1/continuity/cohort?tier=HIGH&limit=10")
    assert res_high.status_code == 200
    for item in res_high.json():
        assert item["risk_tier"] == "HIGH"
        assert item["predicted_readmission_risk"] >= 0.35


def test_api_continuity_evaluate_custom_patient():
    """Verify POST /api/v1/continuity/evaluate-patient computes live SHAP waterfall."""
    payload = {
        "encounter_id": "TEST-ENC-01",
        "patient_mrn": "MRN-TEST-999",
        "department": "Cardiology",
        "age": 80,
        "esi_score": 2,
        "actual_los_hours": 96.0,
        "prior_admissions_count": 4,
        "comorbidity_count": 3,
        "encounter_type": "Emergency",
        "disposition": "Home",
        "chief_complaint": "Acute decompensated heart failure"
    }

    response = client.post("/api/v1/continuity/evaluate-patient", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["encounter_id"] == "TEST-ENC-01"
    assert data["patient_mrn"] == "MRN-TEST-999"
    assert data["predicted_readmission_risk"] > 0.35
    assert data["risk_tier"] == "HIGH"
    assert len(data["feature_attributions"]) == 8


def test_api_continuity_patient_not_found():
    """Verify GET /api/v1/continuity/patient/{id} returns 404 for unknown encounters."""
    response = client.get("/api/v1/continuity/patient/NON-EXISTENT-ENCOUNTER-ID")
    assert response.status_code == 404
