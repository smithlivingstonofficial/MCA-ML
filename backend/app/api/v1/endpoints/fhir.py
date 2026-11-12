"""
Module 1 & 7: HL7 FHIR Release 4 REST Interoperability Endpoints.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.db.models import Encounter, TriageObservation, Bed, Ward, Equipment, UserAccount
from backend.app.domain.fhir_adapter import (
    encounter_to_fhir_r4,
    bed_to_fhir_location,
    equipment_to_fhir_device,
    create_fhir_bundle,
    ingest_fhir_encounter_bundle
)
from backend.app.domain.audit_logger import record_audit_event
from backend.app.schemas.enterprise import FHIRBundleIngestResponse
from backend.app.core.security import get_current_user

router = APIRouter()


@router.post("/bundle", response_model=FHIRBundleIngestResponse)
def ingest_incoming_fhir_bundle(
    bundle: Dict[str, Any] = Body(...),
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ingests an external HL7 FHIR R4 Bundle into the hospital operational database.
    """
    try:
        result = ingest_fhir_encounter_bundle(bundle, db)

        # Audit log the ingestion
        record_audit_event(
            db=db,
            actor_id=current_user.username,
            actor_role=current_user.role,
            action="FHIR_BUNDLE_INGESTION",
            module="Module 1",
            resource_id=f"BUNDLE-ENTRIES-{result['total_entries_processed']}",
            details=f"Processed FHIR Bundle: {result['encounters_ingested']} encounters ingested, {result['locations_acknowledged']} locations referenced."
        )

        return FHIRBundleIngestResponse(
            status="SUCCESS",
            total_entries_processed=result["total_entries_processed"],
            encounters_ingested=result["encounters_ingested"],
            locations_acknowledged=result["locations_acknowledged"],
            message=f"Successfully ingested {result['encounters_ingested']} encounter(s) from standard HL7 FHIR R4 bundle."
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"FHIR Bundle Ingestion failed: {str(e)}")


@router.get("/encounter/{encounter_id}", response_model=Dict[str, Any])
def get_encounter_as_fhir_r4(
    encounter_id: str,
    db: Session = Depends(get_db)
):
    """
    Returns an individual hospital encounter formatted as an HL7 FHIR R4 Encounter resource.
    """
    enc = db.query(Encounter).filter(Encounter.id == encounter_id).first()
    if not enc:
        raise HTTPException(status_code=404, detail=f"Encounter {encounter_id} not found.")

    triage = db.query(TriageObservation).filter(TriageObservation.encounter_id == enc.id).first()
    return encounter_to_fhir_r4(enc, triage)


@router.get("/export/beds", response_model=Dict[str, Any])
def export_beds_as_fhir_locations(db: Session = Depends(get_db)):
    """
    Exports all hospital beds formatted as HL7 FHIR R4 Location resources inside a collection bundle.
    """
    beds = db.query(Bed).all()
    wards_map = {w.id: w for w in db.query(Ward).all()}

    resources: List[Dict[str, Any]] = []
    for b in beds:
        w = wards_map.get(b.ward_id)
        resources.append(bed_to_fhir_location(b, w))

    return create_fhir_bundle(resources)


@router.get("/export/hospital-bundle", response_model=Dict[str, Any])
def export_complete_hospital_fhir_bundle(
    limit_encounters: int = 50,
    current_user: UserAccount = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Exports a comprehensive HL7 FHIR R4 Collection Bundle containing Beds, Equipment, and Encounters.
    """
    beds = db.query(Bed).all()
    wards_map = {w.id: w for w in db.query(Ward).all()}
    equipments = db.query(Equipment).all()
    encounters = db.query(Encounter).order_by(Encounter.arrival_time.desc()).limit(limit_encounters).all()

    resources: List[Dict[str, Any]] = []

    # 1. Beds
    for b in beds:
        resources.append(bed_to_fhir_location(b, wards_map.get(b.ward_id)))

    # 2. Equipment
    for eq in equipments:
        resources.append(equipment_to_fhir_device(eq, wards_map.get(eq.ward_id)))

    # 3. Encounters
    for enc in encounters:
        triage = db.query(TriageObservation).filter(TriageObservation.encounter_id == enc.id).first()
        resources.append(encounter_to_fhir_r4(enc, triage))

    bundle = create_fhir_bundle(resources)

    # Record Audit Event
    record_audit_event(
        db=db,
        actor_id=current_user.username,
        actor_role=current_user.role,
        action="FHIR_BUNDLE_EXPORT",
        module="Module 7",
        resource_id=f"EXPORT-BUNDLE-{len(resources)}",
        details=f"Exported {len(resources)} FHIR R4 resources ({len(beds)} beds, {len(equipments)} devices, {len(encounters)} encounters)."
    )

    return bundle
