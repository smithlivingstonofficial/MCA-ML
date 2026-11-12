export type BedState = 'Ready' | 'Reserved' | 'Occupied' | 'Cleaning' | 'Maintenance' | 'Blocked';

export interface Bed {
  id: string;
  ward_id: string;
  bed_number: string;
  current_state: BedState;
  is_isolation_capable: boolean;
  is_telemetry_capable: boolean;
  last_state_change: string;
}

export interface WardCapacitySummary {
  ward_id: string;
  ward_code: string;
  ward_name: string;
  specialty: string;
  total_physical_beds: number;
  ready_beds: number;
  occupied_beds: number;
  reserved_beds: number;
  cleaning_beds: number;
  maintenance_beds: number;
  blocked_beds: number;
  on_duty_nurses: number;
  nurse_capacity_ceiling: number;
  staffed_usable_beds: number;
  unstaffed_ready_beds: number;
  staffing_deficit: boolean;
  physical_occupancy_rate: number;
  staffed_occupancy_rate: number;
}

export interface HourlyForecastPoint {
  timestamp: string;
  predicted_arrivals: number;
  lower_bound_80: number;
  upper_bound_80: number;
  overcrowding_risk: boolean;
}

export interface ArrivalForecastResponse {
  generated_at: string;
  horizon_hours: number;
  model_version: string;
  data_source: string;
  forecasts: HourlyForecastPoint[];
}

export interface ActiveAlert {
  severity: 'CRITICAL' | 'WARNING' | 'INFO';
  ward_code: string;
  message: string;
  type: string;
}

export interface ExecutiveTelemetry {
  total_census: number;
  total_physical_beds: number;
  total_staffed_beds: number;
  hospital_occupancy_rate: number;
  staffed_occupancy_rate: number;
  active_alerts: ActiveAlert[];
  ed_arrivals_last_24h: number;
  ed_forecast_next_24h: number;
  overcrowding_alert: boolean;
}

// ==================== PHASE 2 TYPES ====================

export interface InventoryLot {
  id: string;
  item_id: string;
  lot_number: string;
  quantity_on_hand: number;
  expiry_date: string;
  received_date: string;
  is_quarantined: boolean;
}

export interface InventoryItem {
  id: string;
  sku_code: string;
  generic_name: string;
  category: string;
  unit_of_measure: string;
  reorder_threshold: number;
  target_stock_level: number;
  standard_lead_time_days: number;
  total_usable_stock: number;
  reorder_required: boolean;
  active_lots: InventoryLot[];
}

export interface DispenseAllocation {
  lot_id: string;
  lot_number: string;
  expiry_date: string;
  quantity_deducted: number;
  remaining_in_lot: number;
}

export interface DispenseResponse {
  sku_code: string;
  generic_name: string;
  requested_qty: number;
  dispensed_allocations: DispenseAllocation[];
  remaining_stock: number;
  reorder_threshold: number;
  reorder_triggered: boolean;
}

export interface VentilatorSummary {
  total: number;
  in_use: number;
  available: number;
  maintenance: number;
  utilization_rate: number;
  utilization_pct: number;
  critical_threshold_exceeded: boolean;
}

export interface OxygenSummary {
  current_volume_liters: number;
  nominal_capacity_liters: number;
  hourly_burn_rate_lph: number;
  days_of_supply_remaining: number;
  capacity_pct: number;
  low_supply_alert: boolean;
}

export interface EquipmentMetrics {
  ventilators: VentilatorSummary;
  oxygen_supply: OxygenSummary;
  fleet_summary: Array<{
    code: string;
    type: string;
    status: string;
    telemetry: string;
    ward_id?: string;
  }>;
}

export interface WardWorkforceSummary {
  ward_id: string;
  ward_code: string;
  ward_name: string;
  specialty: string;
  patient_census: number;
  target_ratio: string;
  required_nurses: number;
  present_nurses: number;
  nurse_deficit: number;
  coverage_pct: number;
  has_deficit: boolean;
}

export interface WorkforceDeficitResponse {
  shift_name: string;
  target_date?: string;
  hospital_coverage_pct: number;
  total_required_nurses: number;
  total_present_nurses: number;
  total_nurse_deficits: number;
  staffing_alerts: Array<{
    severity: string;
    ward_code: string;
    ward_name: string;
    message: string;
    type: string;
  }>;
  ward_summaries: WardWorkforceSummary[];
}

export interface RosterAssignment {
  id: string;
  ward_id: string;
  staff_member_name: string;
  role: string;
  shift_name: string;
  shift_date: string;
  status: string;
  is_on_duty: boolean;
}

// ==================== PHASE 3 TYPES ====================

export interface BedAssignment {
  patient_id: string;
  patient_anon_id: string;
  esi_score: number;
  bed_id: string;
  bed_number: string;
  ward_id: string;
  ward_name: string;
  specialty: string;
  is_isolation_certified: boolean;
}

export interface OptimizationResponse {
  status: string;
  solver_message: string;
  total_patients: number;
  assigned_count: number;
  unassigned_count: number;
  execution_time_ms: number;
  objective_value: number;
  assignments: BedAssignment[];
  unassigned_patients: Array<{
    id: string;
    patient_anon_id?: string;
    esi_score?: number;
    chief_complaint?: string;
  }>;
  diagnostics: string[];
}

export interface ScenarioMetrics {
  arrivals_24h: number;
  total_staffed_capacity: number;
  ready_beds: number;
  staffed_occupancy_pct: number;
  hospital_stress_index?: number;
  is_critical_overcapacity?: boolean;
  ward_breakdown: Array<{
    ward_code: string;
    ward_name: string;
    staffed_usable: number;
    occupancy_rate: number;
    deficit?: boolean;
  }>;
}

export interface SimulationResponse {
  parameters: {
    arrival_surge_multiplier: number;
    nurse_absenteeism_pct: number;
    out_of_service_bed_pct: number;
    horizon_hours: number;
  };
  baseline: ScenarioMetrics;
  simulated: ScenarioMetrics;
  recommendations: string[];
}

export interface CrisisTemplate {
  template_key: string;
  name: string;
  description: string;
  arrival_surge_multiplier: number;
  nurse_absenteeism_pct: number;
  out_of_service_bed_pct: number;
}

// ==================== MODULE 6: CARE CONTINUITY & SHAP EXPLAINABILITY ====================

export interface FeatureAttributionItem {
  feature_name: string;
  display_name: string;
  feature_value: number;
  shap_value: number;
  effect: 'risk_increasing' | 'protective' | 'neutral';
  clinical_interpretation: string;
}

export interface PatientCohortItem {
  encounter_id: string;
  patient_mrn: string;
  patient_age: number;
  department: string;
  disposition: string;
  actual_los_hours: number;
  predicted_readmission_risk: number;
  predicted_noshow_risk?: number | null;
  risk_tier: 'HIGH' | 'MODERATE' | 'LOW';
  recommended_outreach: string;
}

export interface PatientRiskEvaluation {
  encounter_id: string;
  patient_mrn: string;
  patient_age: number;
  department: string;
  predicted_readmission_risk: number;
  predicted_noshow_risk?: number | null;
  risk_tier: 'HIGH' | 'MODERATE' | 'LOW';
  base_log_odds: number;
  recommended_outreach: string;
  feature_attributions: FeatureAttributionItem[];
}

export interface ContinuityOverviewResponse {
  total_cohort_evaluated: number;
  high_risk_count: number;
  moderate_risk_count: number;
  low_risk_count: number;
  mean_readmission_risk: number;
  high_risk_patients: PatientCohortItem[];
}

export interface EvaluatePatientRequest {
  encounter_id?: string;
  patient_mrn?: string;
  department?: string;
  age: number;
  esi_score: number;
  actual_los_hours: number;
  prior_admissions_count: number;
  comorbidity_count: number;
  encounter_type?: string;
  disposition?: string;
  chief_complaint?: string;
}

// ==================== MODULE 7: MODEL GOVERNANCE & DRIFT ====================

export interface FeatureDriftMetric {
  psi: number;
  status: 'STABLE' | 'MODERATE_DRIFT' | 'CRITICAL_DRIFT';
  ks_statistic: number;
  ks_p_value: number;
  drift_detected: boolean;
}

export interface DataQualitySummary {
  records_audited: number;
  quality_score_pct: number;
  timestamp_anomalies: number;
  range_anomalies: number;
  missing_critical_fields: number;
  integrity_passed: boolean;
}

export interface ModelRegistryItem {
  module: string;
  model_name: string;
  architecture: string;
  version: string;
  last_trained?: string;
  validation_wape?: number;
  validation_roc_auc?: number;
  status: string;
}

export interface ModelGovernanceResponse {
  evaluated_at: string;
  overall_governance_status: 'STABLE' | 'MODERATE_DRIFT' | 'CRITICAL_DRIFT';
  active_models: ModelRegistryItem[];
  features: Record<string, FeatureDriftMetric>;
  data_quality: DataQualitySummary;
  recommendation: string;
}

// ==================== PHASE 6: ENTERPRISE SECURITY, FHIR & AUDIT ====================

export interface UserProfileResponse {
  id: string;
  username: string;
  full_name: string;
  role: string;
  department?: string | null;
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: UserProfileResponse;
}

export interface RoleInfo {
  role_key: string;
  title: string;
  description: string;
  demo_username: string;
  permissions: string[];
}

export interface AuditLogItem {
  id: string;
  timestamp: string;
  actor_id: string;
  actor_role: string;
  action: string;
  module: string;
  resource_id?: string | null;
  details: string;
  status: string;
  ip_address: string;
}

export interface AuditLogResponse {
  total_events: number;
  events: AuditLogItem[];
}

export interface FHIRBundleIngestResponse {
  status: string;
  total_entries_processed: number;
  encounters_ingested: number;
  locations_acknowledged: number;
  message: string;
}

export interface ExecutiveBriefResponse {
  generated_at: string;
  hospital_name: string;
  total_physical_beds: number;
  total_staffed_beds: number;
  hospital_occupancy_pct: number;
  staffed_occupancy_pct: number;
  ed_arrivals_past_24h: number;
  ed_forecast_next_24h: number;
  overcrowding_surge_risk: boolean;
  oxygen_days_remaining: number;
  ventilator_utilization_pct: number;
  critical_staffing_deficits: number;
  high_readmission_risk_cohort_count: number;
  model_governance_status: string;
  active_alerts_count: number;
}

// ==================== PHASE 7: REAL-TIME WEBSOCKETS, ANOMALIES & COPILOT ====================

export interface WebSocketEventMessage {
  event_id: string;
  event_type: string;
  timestamp: string;
  module: string;
  severity: 'INFO' | 'WARNING' | 'CRITICAL';
  message: string;
  payload?: Record<string, any>;
}

export interface OperationalAnomalyItem {
  anomaly_id: string;
  category: string;
  severity: 'CRITICAL' | 'WARNING' | 'INFO';
  target_entity: string;
  detected_value: number;
  expected_baseline: number;
  z_score: number;
  anomaly_score: number;
  title: string;
  root_cause_analysis: string;
  detected_at: string;
}

export interface AnomalyDetectionResponse {
  evaluated_at: string;
  anomalies_detected_count: number;
  critical_count: number;
  warning_count: number;
  overall_operational_health_score: number;
  anomalies: OperationalAnomalyItem[];
  diagnostic_summary: string;
}

export interface CopilotRecommendationItem {
  recommendation_id: string;
  urgency: 'IMMEDIATE' | 'HIGH' | 'MEDIUM';
  category: string;
  title: string;
  rationalization: string;
  recommended_action: string;
  projected_impact: string;
  status: 'PENDING' | 'ACKNOWLEDGED' | 'DISPATCHED';
  target_department: string;
  created_at: string;
}

export interface CopilotRecommendationsResponse {
  total_recommendations: number;
  immediate_actions_count: number;
  recommendations: CopilotRecommendationItem[];
}

export interface CopilotActionResponse {
  recommendation_id: string;
  status: string;
  dispatched_at: string;
  actor_id: string;
  message: string;
}




