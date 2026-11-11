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
