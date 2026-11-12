"""
Phase 8: Multi-Hospital Regional Coordination & Transfer Optimization Schemas.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class HospitalFacilityTelemetry(BaseModel):
    hospital_id: str
    hospital_name: str
    facility_type: str  # "LEVEL_1_TRAUMA_HUB", "REGIONAL_COMMUNITY", "SURGICAL_SPECIALTY", "URGENT_OBSERVATION"
    location: str
    total_physical_beds: int
    staffed_usable_beds: int
    occupied_beds: int
    available_beds: int
    staffed_occupancy_pct: float
    icu_occupancy_pct: float
    ed_wait_time_minutes: int
    ed_arrivals_past_24h: int
    diversion_status: str  # "NORMAL", "ADVISORY", "DIVERT_OVERFLOW", "CRITICAL_LOCKDOWN"
    specialties_available: List[str]
    latitude: float
    longitude: float


class TransitMatrixItem(BaseModel):
    origin_hospital_id: str
    destination_hospital_id: str
    distance_km: float
    transit_time_minutes: int


class RegionalNetworkStatusResponse(BaseModel):
    evaluated_at: datetime
    network_name: str
    total_facilities: int
    network_physical_beds: int
    network_staffed_beds: int
    network_occupied_beds: int
    network_occupancy_pct: float
    network_stress_index: float  # 0.0 to 100.0
    active_diversions_count: int
    facilities: List[HospitalFacilityTelemetry]
    transit_matrix: List[TransitMatrixItem]


class InterFacilityTransferRecommendation(BaseModel):
    transfer_id: str
    urgency: str  # "IMMEDIATE", "HIGH", "SCHEDULED"
    source_hospital_id: str
    source_hospital_name: str
    destination_hospital_id: str
    destination_hospital_name: str
    patient_anon_id: str
    triage_acuity: str  # ESI 1 to 5
    specialty_required: str
    transit_distance_km: float
    transit_time_minutes: int
    clinical_justification: str
    projected_load_relief_pct: float
    status: str  # "RECOMMENDED", "APPROVED", "DISPATCHED"


class RegionalTransferOptimizationResponse(BaseModel):
    computed_at: datetime
    solver_status: str
    total_transfers_recommended: int
    estimated_network_occupancy_post_transfer: float
    transfers: List[InterFacilityTransferRecommendation]
    optimization_summary: str


class DispatchTransferRequest(BaseModel):
    transfer_id: str
    notes: Optional[str] = "Approved by Regional Bed Coordination Desk"
    transport_vehicle_type: Optional[str] = "CRITICAL_CARE_AMBULANCE"


class DispatchTransferResponse(BaseModel):
    transfer_id: str
    status: str
    dispatched_at: datetime
    dispatched_by: str
    message: str
    source_hospital: str
    destination_hospital: str


class ToggleDiversionRequest(BaseModel):
    hospital_id: str
    new_status: str  # "NORMAL", "DIVERT_OVERFLOW"
    reason: Optional[str] = "Overcrowding mitigation protocol triggered"


class ToggleDiversionResponse(BaseModel):
    hospital_id: str
    previous_status: str
    new_status: str
    updated_at: datetime
    updated_by: str
    broadcast_event_id: str
    message: str
