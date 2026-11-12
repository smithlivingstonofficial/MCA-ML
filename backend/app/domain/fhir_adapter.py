"""
Module 1 & 7: HL7 FHIR R4 Interoperability Adapter.
Transforms hospital canonical operational entities (Encounters, Beds, Equipment)
to and from HL7 FHIR Release 4 standard specifications.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.db.models import Encounter, TriageObservation, Bed, Ward, Equipment


def encounter_to_fhir_r4(
    encounter: Encounter,
    triage: Optional[TriageObservation] = None
) -> Dict[str, Any]:
    """
    Transforms an internal hospital Encounter into a standard HL7 FHIR R4 Encounter resource.
    """
    is_emergency = encounter.encounter_type == "Emergency"
    enc_status = "finished" if encounter.discharge_time else "in-progress"

    # HL7 ActEncounterCode
    class_code = "EMER" if is_emergency else "IMP"
    class_display = "emergency" if is_emergency else "inpatient encounter"

    # Map ESI acuity to FHIR v3-ActPriority
    priority_coding = None
    if triage:
        esi = triage.esi_score
        if esi == 1:
            priority_coding = {"code": "CR", "display": "Critical / Resuscitation"}
        elif esi == 2:
            priority_coding = {"code": "EM", "display": "Emergency"}
        elif esi == 3:
            priority_coding = {"code": "UR", "display": "Urgent"}
        else:
            priority_coding = {"code": "R", "display": "Routine"}

    resource: Dict[str, Any] = {
        "resourceType": "Encounter",
        "id": encounter.id,
        "identifier": [
            {
                "use": "usual",
                "system": "urn:oid:hospital:patient-pseudonym",
                "value": f"MRN-{encounter.patient_anon_id[:8].upper()}"
            }
        ],
        "status": enc_status,
        "class": {
            "system": "http://terminology.hl7.org/CodeSystem/v3-ActEncounterCode",
            "code": class_code,
            "display": class_display
        },
        "period": {
            "start": encounter.arrival_time.isoformat() if encounter.arrival_time else None,
            "end": encounter.discharge_time.isoformat() if encounter.discharge_time else None
        },
        "reasonCode": [
            {
                "text": triage.chief_complaint if triage else (encounter.primary_diagnosis_category or "Acute Care")
            }
        ],
        "hospitalization": {
            "dischargeDisposition": {
                "text": encounter.disposition or "Discharged"
            }
        }
    }

    if priority_coding:
        resource["priority"] = {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ActPriority",
                    "code": priority_coding["code"],
                    "display": priority_coding["display"]
                }
            ]
        }

    return resource


def bed_to_fhir_location(
    bed: Bed,
    ward: Optional[Ward] = None
) -> Dict[str, Any]:
    """
    Transforms an internal Bed into a standard HL7 FHIR R4 Location resource.
    Operational bed states mapped to HL7 Table 0116 Bed Status codes.
    """
    status_map = {
        "Ready": ("U", "Unoccupied"),
        "Reserved": ("U", "Reserved"),
        "Occupied": ("O", "Occupied"),
        "Cleaning": ("K", "Contaminated/Cleaning"),
        "Maintenance": ("I", "Isolated/Maintenance"),
        "Blocked": ("BL", "Blocked")
    }

    code, display = status_map.get(bed.current_state, ("U", "Unoccupied"))
    is_active = bed.current_state in ["Ready", "Reserved", "Occupied"]

    resource: Dict[str, Any] = {
        "resourceType": "Location",
        "id": bed.id,
        "identifier": [
            {
                "system": "urn:oid:hospital:bed-number",
                "value": bed.bed_number
            }
        ],
        "status": "active" if is_active else "suspended",
        "operationalStatus": {
            "system": "http://terminology.hl7.org/CodeSystem/v2-0116",
            "code": code,
            "display": display
        },
        "mode": "instance",
        "physicalType": {
            "coding": [
                {
                    "system": "http://terminology.hl7.org/CodeSystem/location-physical-type",
                    "code": "bd",
                    "display": "Bed"
                }
            ]
        }
    }

    if ward:
        resource["partOf"] = {
            "reference": f"Location/{ward.id}",
            "display": f"{ward.name} ({ward.specialty})"
        }

    return resource


def equipment_to_fhir_device(
    eq: Equipment,
    ward: Optional[Ward] = None
) -> Dict[str, Any]:
    """
    Transforms hospital medical equipment into an HL7 FHIR R4 Device resource.
    """
    return {
        "resourceType": "Device",
        "id": eq.id,
        "identifier": [
            {
                "system": "urn:oid:hospital:equipment-code",
                "value": eq.equipment_code
            }
        ],
        "status": "active" if eq.status == "In_Use" else "available",
        "type": {
            "text": eq.equipment_type
        },
        "location": {
            "reference": f"Location/{ward.id}" if ward else None,
            "display": ward.name if ward else "Central Medical Equipment Depot"
        }
    }


def create_fhir_bundle(resources: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Bundles multiple FHIR resources into a compliant HL7 FHIR R4 Collection Bundle.
    """
    entries = []
    for res in resources:
        entries.append({
            "fullUrl": f"urn:uuid:{res.get('id', 'anon')}",
            "resource": res
        })

    return {
        "resourceType": "Bundle",
        "type": "collection",
        "timestamp": datetime.utcnow().isoformat(),
        "total": len(entries),
        "entry": entries
    }


def ingest_fhir_encounter_bundle(
    bundle: Dict[str, Any],
    db: Session
) -> Dict[str, Any]:
    """
    Validates and ingests an external HL7 FHIR R4 Bundle into the operational database.
    """
    if bundle.get("resourceType") != "Bundle":
        raise ValueError("Invalid payload: payload must be an HL7 FHIR R4 'Bundle'.")

    entries = bundle.get("entry", [])
    ingested_encounters = 0
    ingested_locations = 0

    for item in entries:
        res = item.get("resource", {})
        rtype = res.get("resourceType")

        if rtype == "Encounter":
            # Extract identifier and period
            ident_list = res.get("identifier", [])
            anon_id = ident_list[0].get("value", "FHIR-PATIENT-ANON") if ident_list else "FHIR-PATIENT-ANON"
            period = res.get("period", {})
            start_str = period.get("start")
            arrival_dt = datetime.fromisoformat(start_str.replace("Z", "+00:00")).replace(tzinfo=None) if start_str else datetime.utcnow()

            cls_obj = res.get("class", {})
            enc_type = "Emergency" if cls_obj.get("code") == "EMER" else "Inpatient"

            new_enc = Encounter(
                patient_anon_id=anon_id,
                encounter_type=enc_type,
                arrival_time=arrival_dt,
                disposition="Admitted"
            )
            db.add(new_enc)
            ingested_encounters += 1

        elif rtype == "Location":
            ingested_locations += 1

    db.commit()

    return {
        "status": "SUCCESS",
        "total_entries_processed": len(entries),
        "encounters_ingested": ingested_encounters,
        "locations_acknowledged": ingested_locations
    }
