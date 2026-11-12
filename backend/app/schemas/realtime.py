"""
Pydantic schemas for Phase 7: Real-Time WebSockets, Anomaly Detection & AI Decision Support Copilot.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


# ==================== WEBSOCKET & STREAM SCHEMAS ====================

class WebSocketEventMessage(BaseModel):
    event_id: str
    event_type: str  # SURGE_ALERT, BED_STATE_CHANGE, ANOMALY_DETECTED, COPILOT_RECOMMENDATION, DISPENSE_EVENT
    timestamp: datetime
    module: str
    severity: str = "INFO"  # INFO, WARNING, CRITICAL
    message: str
    payload: Dict[str, Any] = {}


class TriggerStreamEventRequest(BaseModel):
    event_type: str = "SURGE_ALERT"
    module: str = "Module 1"
    severity: str = "WARNING"
    message: str = "Simulated Emergency Department arrival surge detected."
    payload: Dict[str, Any] = {}


# ==================== ANOMALY DETECTION SCHEMAS ====================

class OperationalAnomalyItem(BaseModel):
    anomaly_id: str
    category: str  # TRIAGE_DELAY, BED_HOARDING, RAPID_DISCHARGE, MED_BURN_SPIKE, O2_PRESSURE_DROP
    severity: str  # CRITICAL, WARNING, INFO
    target_entity: str  # Ward code, SKU, or Department
    detected_value: float
    expected_baseline: float
    z_score: float
    anomaly_score: float = Field(ge=0.0, le=1.0)
    title: str
    root_cause_analysis: str
    detected_at: datetime


class AnomalyDetectionResponse(BaseModel):
    evaluated_at: datetime
    anomalies_detected_count: int
    critical_count: int
    warning_count: int
    overall_operational_health_score: float  # 0 to 100
    anomalies: List[OperationalAnomalyItem]
    diagnostic_summary: str


# ==================== AI COPILOT SCHEMAS ====================

class CopilotRecommendationItem(BaseModel):
    recommendation_id: str
    urgency: str  # IMMEDIATE, HIGH, MEDIUM
    category: str  # BED_REBALANCING, STAFF_DISPATCH, PHARMACY_REPLENISH, OXYGEN_SAFETY, FLOW_DIVERSION
    title: str
    rationalization: str
    recommended_action: str
    projected_impact: str
    status: str  # PENDING, ACKNOWLEDGED, DISPATCHED
    target_department: str
    created_at: datetime


class CopilotRecommendationsResponse(BaseModel):
    total_recommendations: int
    immediate_actions_count: int
    recommendations: List[CopilotRecommendationItem]


class CopilotActionRequest(BaseModel):
    actor_id: str = "admin"
    actor_role: str = "HOSPITAL_ADMIN"
    notes: Optional[str] = "Approved mitigation protocol for immediate execution."


class CopilotActionResponse(BaseModel):
    recommendation_id: str
    status: str
    dispatched_at: datetime
    actor_id: str
    message: str
