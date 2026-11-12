"""
Module 7 Tests: Phase 6 Enterprise Interoperability, HL7 FHIR R4, Security & Audit Trail.
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.core.security import create_token, HealthcareRole
from backend.app.domain.fhir_adapter import create_fhir_bundle

client = TestClient(app)


def test_auth_login_success_and_failure():
    """Verify that valid healthcare credentials issue signed tokens and invalid reject with 401."""
    # 1. Valid login
    res = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "Bearer"
    assert data["user"]["role"] == HealthcareRole.HOSPITAL_ADMIN

    # 2. Invalid password
    res_bad = client.post("/api/v1/auth/login", json={"username": "admin", "password": "wrongpassword"})
    assert res_bad.status_code == 401

    # 3. Nonexistent user
    res_none = client.post("/api/v1/auth/login", json={"username": "fake_doctor", "password": "password"})
    assert res_none.status_code == 401


def test_auth_roles_endpoint():
    """Verify GET /api/v1/auth/roles returns documentation and demo credentials for 4 healthcare roles."""
    res = client.get("/api/v1/auth/roles")
    assert res.status_code == 200
    roles = res.json()
    assert len(roles) == 4
    role_keys = [r["role_key"] for r in roles]
    assert HealthcareRole.HOSPITAL_ADMIN in role_keys
    assert HealthcareRole.BED_MANAGER in role_keys
    assert HealthcareRole.PHARMACIST in role_keys
    assert HealthcareRole.CLINICAL_REVIEWER in role_keys


def test_fhir_export_beds_bundle():
    """Verify GET /api/v1/fhir/export/beds produces a compliant HL7 FHIR R4 Location Collection Bundle."""
    res = client.get("/api/v1/fhir/export/beds")
    assert res.status_code == 200
    bundle = res.json()

    assert bundle["resourceType"] == "Bundle"
    assert bundle["type"] == "collection"
    assert bundle["total"] > 0
    assert len(bundle["entry"]) > 0

    first_resource = bundle["entry"][0]["resource"]
    assert first_resource["resourceType"] == "Location"
    assert "identifier" in first_resource
    assert "operationalStatus" in first_resource
    assert first_resource["operationalStatus"]["system"] == "http://terminology.hl7.org/CodeSystem/v2-0116"


def test_fhir_export_hospital_bundle():
    """Verify GET /api/v1/fhir/export/hospital-bundle exports Beds, Devices, and Encounters."""
    token = create_token({"sub": "admin", "role": HealthcareRole.HOSPITAL_ADMIN})
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/v1/fhir/export/hospital-bundle?limit_encounters=10", headers=headers)
    assert res.status_code == 200
    bundle = res.json()

    assert bundle["resourceType"] == "Bundle"
    assert bundle["total"] > 0

    resource_types = {e["resource"]["resourceType"] for e in bundle["entry"]}
    assert "Location" in resource_types
    assert "Encounter" in resource_types or "Device" in resource_types


def test_fhir_bundle_ingestion():
    """Verify POST /api/v1/fhir/bundle ingests an external HL7 FHIR R4 collection bundle."""
    token = create_token({"sub": "admin", "role": HealthcareRole.HOSPITAL_ADMIN})
    headers = {"Authorization": f"Bearer {token}"}

    test_bundle = {
        "resourceType": "Bundle",
        "type": "collection",
        "entry": [
            {
                "fullUrl": "urn:uuid:TEST-FHIR-ENC-001",
                "resource": {
                    "resourceType": "Encounter",
                    "id": "FHIR-TEST-001",
                    "identifier": [{"value": "MRN-FHIR-INGEST-01"}],
                    "status": "in-progress",
                    "class": {"code": "EMER"},
                    "period": {"start": "2026-11-12T10:00:00Z"}
                }
            }
        ]
    }

    res = client.post("/api/v1/fhir/bundle", json=test_bundle, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "SUCCESS"
    assert data["encounters_ingested"] >= 1


def test_audit_trail_logging_and_retrieval():
    """Verify audit logs are recorded and filterable via GET /api/v1/audit/logs."""
    token = create_token({"sub": "admin", "role": HealthcareRole.HOSPITAL_ADMIN})
    headers = {"Authorization": f"Bearer {token}"}

    # Record a custom compliance event
    payload = {
        "action": "STERILITY_BATCH_VERIFICATION",
        "module": "Module 3",
        "resource_id": "LOT-STERILE-999",
        "details": "Terminal cleanroom autoclave sterilization verified with bio-indicator.",
        "status": "SUCCESS"
    }

    post_res = client.post("/api/v1/audit/log", json=payload, headers=headers)
    assert post_res.status_code == 200
    created = post_res.json()
    assert created["action"] == "STERILITY_BATCH_VERIFICATION"

    # Query audit logs
    get_res = client.get("/api/v1/audit/logs?action=STERILITY_BATCH_VERIFICATION")
    assert get_res.status_code == 200
    audit_data = get_res.json()
    assert audit_data["total_events"] >= 1
    assert any(e["action"] == "STERILITY_BATCH_VERIFICATION" for e in audit_data["events"])


def test_executive_reports_endpoints():
    """Verify executive summary and CSV report streams."""
    # 1. Executive Brief JSON
    brief_res = client.get("/api/v1/reports/executive-brief")
    assert brief_res.status_code == 200
    brief = brief_res.json()
    assert "total_physical_beds" in brief
    assert "hospital_occupancy_pct" in brief
    assert "oxygen_days_remaining" in brief
    assert "model_governance_status" in brief

    # 2. Readmission Cohort CSV
    csv_res = client.get("/api/v1/reports/readmission-cohort.csv")
    assert csv_res.status_code == 200
    assert "text/csv" in csv_res.headers["content-type"]
    content = csv_res.text
    assert "Encounter_ID,Patient_MRN" in content

    # 3. Bed Occupancy CSV
    bed_csv_res = client.get("/api/v1/reports/bed-occupancy.csv")
    assert bed_csv_res.status_code == 200
    assert "text/csv" in bed_csv_res.headers["content-type"]
    assert "Ward_Code,Ward_Name" in bed_csv_res.text
