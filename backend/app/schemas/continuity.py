"""
Pydantic schemas for Module 6: Patient Continuity and Post-Discharge Risk Intelligence.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class FeatureAttributionItem(BaseModel):
    feature_name: str
    display_name: str
    feature_value: float
    shap_value: float
    effect: str
    clinical_interpretation: str


class PatientCohortItem(BaseModel):
    encounter_id: str
    patient_mrn: str
    patient_age: int
    department: str
    disposition: str
    actual_los_hours: float
    predicted_readmission_risk: float
    predicted_noshow_risk: Optional[float] = None
    risk_tier: str
    recommended_outreach: str


class PatientRiskEvaluation(BaseModel):
    encounter_id: str
    patient_mrn: str
    patient_age: int
    department: str
    predicted_readmission_risk: float
    predicted_noshow_risk: Optional[float] = None
    risk_tier: str
    base_log_odds: float
    recommended_outreach: str
    feature_attributions: List[FeatureAttributionItem]


class ContinuityOverviewResponse(BaseModel):
    total_cohort_evaluated: int
    high_risk_count: int
    moderate_risk_count: int
    low_risk_count: int
    mean_readmission_risk: float
    high_risk_patients: List[PatientCohortItem]


class EvaluatePatientRequest(BaseModel):
    encounter_id: Optional[str] = "ENC-CUSTOM-001"
    patient_mrn: Optional[str] = "MRN-SIM-999"
    department: Optional[str] = "General Medicine"
    age: int = Field(default=68, ge=0, le=120)
    esi_score: int = Field(default=3, ge=1, le=5)
    actual_los_hours: float = Field(default=48.0, ge=0.0)
    prior_admissions_count: int = Field(default=2, ge=0)
    comorbidity_count: int = Field(default=2, ge=0)
    encounter_type: str = "Emergency"
    disposition: str = "Home"
    chief_complaint: str = "Shortness of breath and chest pressure"
