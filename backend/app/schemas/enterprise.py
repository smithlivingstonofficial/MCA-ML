"""
Pydantic schemas for Phase 6: Enterprise Security, HL7 FHIR, Audit Logs & Reporting.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# ==================== AUTH & RBAC SCHEMAS ====================

class LoginRequest(BaseModel):
    username: str
    password: str


class UserProfileResponse(BaseModel):
    id: str
    username: str
    full_name: str
    role: str
    department: Optional[str] = None
    is_active: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    user: UserProfileResponse


class RoleInfo(BaseModel):
    role_key: str
    title: str
    description: str
    demo_username: str
    permissions: List[str]


# ==================== AUDIT SCHEMAS ====================

class AuditLogItem(BaseModel):
    id: str
    timestamp: datetime
    actor_id: str
    actor_role: str
    action: str
    module: str
    resource_id: Optional[str] = None
    details: str
    status: str
    ip_address: str


class AuditLogResponse(BaseModel):
    total_events: int
    events: List[AuditLogItem]


class RecordAuditRequest(BaseModel):
    action: str
    module: str
    resource_id: Optional[str] = None
    details: str
    status: str = "SUCCESS"


# ==================== FHIR SCHEMAS ====================

class FHIRBundleIngestResponse(BaseModel):
    status: str
    total_entries_processed: int
    encounters_ingested: int
    locations_acknowledged: int
    message: str


# ==================== EXECUTIVE REPORT SCHEMAS ====================

class ExecutiveBriefResponse(BaseModel):
    generated_at: datetime
    hospital_name: str
    total_physical_beds: int
    total_staffed_beds: int
    hospital_occupancy_pct: float
    staffed_occupancy_pct: float
    ed_arrivals_past_24h: int
    ed_forecast_next_24h: int
    overcrowding_surge_risk: bool
    oxygen_days_remaining: float
    ventilator_utilization_pct: float
    critical_staffing_deficits: int
    high_readmission_risk_cohort_count: int
    model_governance_status: str
    active_alerts_count: int
