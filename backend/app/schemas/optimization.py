from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class PatientCandidate(BaseModel):
    id: str
    patient_anon_id: str
    esi_score: int = Field(..., ge=1, le=5)
    chief_complaint: str
    waiting_time_minutes: float = 0.0
    requires_icu: bool = False
    requires_isolation: bool = False
    preferred_ward_id: Optional[str] = None


class BedAssignmentResult(BaseModel):
    patient_id: str
    patient_anon_id: str
    esi_score: int
    bed_id: str
    bed_number: str
    ward_id: str
    ward_name: str
    specialty: str
    is_isolation_certified: bool


class OptimizationRunResponse(BaseModel):
    status: str
    solver_message: str
    total_patients: int
    assigned_count: int
    unassigned_count: int
    execution_time_ms: float
    objective_value: float
    assignments: List[BedAssignmentResult]
    unassigned_patients: List[Dict[str, Any]]
    diagnostics: List[str]


class SimulationRequest(BaseModel):
    arrival_surge_multiplier: float = Field(1.0, ge=0.5, le=3.0)
    nurse_absenteeism_pct: float = Field(0.0, ge=0.0, le=0.6)
    out_of_service_bed_pct: float = Field(0.0, ge=0.0, le=0.5)
    horizon_hours: int = Field(24, ge=12, le=72)


class ScenarioMetrics(BaseModel):
    arrivals_24h: int
    total_staffed_capacity: int
    ready_beds: int
    staffed_occupancy_pct: float
    hospital_stress_index: Optional[float] = None
    is_critical_overcapacity: Optional[bool] = None
    ward_breakdown: List[Dict[str, Any]]


class SimulationResponse(BaseModel):
    parameters: Dict[str, Any]
    baseline: ScenarioMetrics
    simulated: ScenarioMetrics
    recommendations: List[str]


class CrisisTemplateResponse(BaseModel):
    template_key: str
    name: str
    description: str
    arrival_surge_multiplier: float
    nurse_absenteeism_pct: float
    out_of_service_bed_pct: float

