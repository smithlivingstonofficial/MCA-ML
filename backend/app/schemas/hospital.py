from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from backend.app.domain.bed_lifecycle import BedState


class BedBase(BaseModel):
    bed_number: str
    ward_id: str
    current_state: BedState = BedState.READY
    is_isolation_capable: bool = False
    is_telemetry_capable: bool = False


class BedStateUpdate(BaseModel):
    new_state: BedState
    reason: Optional[str] = None
    operator_id: str = "operator"


class BedResponse(BedBase):
    id: str
    last_state_change: datetime

    model_config = ConfigDict(from_attributes=True)


class WardResponse(BaseModel):
    id: str
    department_id: str
    code: str
    name: str
    specialty: str
    total_physical_beds: int
    target_nurse_to_patient_ratio: float

    model_config = ConfigDict(from_attributes=True)


class WardCapacitySummary(BaseModel):
    ward_id: str
    ward_code: str
    ward_name: str
    specialty: str
    total_physical_beds: int
    ready_beds: int
    occupied_beds: int
    reserved_beds: int
    cleaning_beds: int
    maintenance_beds: int
    blocked_beds: int
    on_duty_nurses: int
    nurse_capacity_ceiling: int
    staffed_usable_beds: int
    unstaffed_ready_beds: int
    staffing_deficit: bool
    physical_occupancy_rate: float
    staffed_occupancy_rate: float


class HourlyForecastPoint(BaseModel):
    timestamp: datetime
    predicted_arrivals: float
    lower_bound_80: float
    upper_bound_80: float
    overcrowding_risk: bool


class ArrivalForecastResponse(BaseModel):
    generated_at: datetime
    horizon_hours: int
    model_version: str
    data_source: str = "SYNTHETIC DEMO DATA"
    forecasts: List[HourlyForecastPoint]


class ExecutiveOverviewResponse(BaseModel):
    total_census: int
    total_physical_beds: int
    total_staffed_beds: int
    hospital_occupancy_rate: float
    staffed_occupancy_rate: float
    active_alerts: List[Dict[str, Any]]
    ed_arrivals_last_24h: int
    ed_forecast_next_24h: int
    overcrowding_alert: bool = False


class FeatureDriftMetric(BaseModel):
    psi: float
    status: str
    ks_statistic: float
    ks_p_value: float
    drift_detected: bool


class DataQualitySummary(BaseModel):
    records_audited: int
    quality_score_pct: float
    timestamp_anomalies: int
    range_anomalies: int
    missing_critical_fields: int
    integrity_passed: bool


class ModelGovernanceResponse(BaseModel):
    evaluated_at: datetime
    overall_governance_status: str
    active_models: List[Dict[str, Any]]
    features: Dict[str, FeatureDriftMetric]
    data_quality: DataQualitySummary
    recommendation: str


