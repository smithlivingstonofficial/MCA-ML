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
