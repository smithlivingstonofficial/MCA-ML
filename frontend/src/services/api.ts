import axios from 'axios';
import {
  ExecutiveTelemetry,
  WardCapacitySummary,
  Bed,
  ArrivalForecastResponse,
  BedState,
  InventoryItem,
  InventoryLot,
  DispenseResponse,
  EquipmentMetrics,
  WorkforceDeficitResponse,
  RosterAssignment,
  OptimizationResponse,
  SimulationResponse,
  CrisisTemplate,
  ContinuityOverviewResponse,
  PatientCohortItem,
  PatientRiskEvaluation,
  EvaluatePatientRequest
} from '../types';

const API_BASE = '/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ==================== PHASE 1 APIS ====================

export const fetchTelemetryOverview = async (): Promise<ExecutiveTelemetry> => {
  const { data } = await apiClient.get<ExecutiveTelemetry>('/telemetry/overview');
  return data;
};

export const fetchWardCapacities = async (): Promise<WardCapacitySummary[]> => {
  const { data } = await apiClient.get<WardCapacitySummary[]>('/beds/capacity');
  return data;
};

export const fetchBeds = async (wardId?: string): Promise<Bed[]> => {
  const { data } = await apiClient.get<Bed[]>('/beds', {
    params: wardId ? { ward_id: wardId } : {},
  });
  return data;
};

export const updateBedState = async (
  bedId: string,
  newState: BedState,
  reason: string = 'Operational update'
): Promise<Bed> => {
  const { data } = await apiClient.patch<Bed>(`/beds/${bedId}/state`, {
    new_state: newState,
    reason: reason,
    operator_id: 'COMMAND_CENTER_ADMIN',
  });
  return data;
};

export const fetchArrivalForecast = async (
  horizon: number = 24
): Promise<ArrivalForecastResponse> => {
  const { data } = await apiClient.get<ArrivalForecastResponse>('/arrivals/forecast', {
    params: { horizon },
  });
  return data;
};

// ==================== PHASE 2 APIS ====================

export const fetchInventoryItems = async (category?: string, lowStockOnly: boolean = false): Promise<InventoryItem[]> => {
  const { data } = await apiClient.get<InventoryItem[]>('/inventory/items', {
    params: {
      category: category && category !== 'ALL' ? category : undefined,
      low_stock_only: lowStockOnly,
    },
  });
  return data;
};

export const fetchInventoryLots = async (skuCode?: string): Promise<InventoryLot[]> => {
  const { data } = await apiClient.get<InventoryLot[]>('/inventory/lots', {
    params: skuCode ? { sku_code: skuCode } : {},
  });
  return data;
};

export const dispenseMedication = async (
  skuCode: string,
  requestedQty: number,
  dispensedBy: string = 'PHARMACY_STAFF'
): Promise<DispenseResponse> => {
  const { data } = await apiClient.post<DispenseResponse>('/inventory/dispense', {
    sku_code: skuCode,
    requested_qty: requestedQty,
    dispensed_by: dispensedBy,
    reason: 'Prescription fulfillment',
  });
  return data;
};

export const fetchEquipmentTelemetry = async (): Promise<EquipmentMetrics> => {
  const { data } = await apiClient.get<EquipmentMetrics>('/inventory/equipment-telemetry');
  return data;
};

export const fetchWorkforceDeficits = async (shift: string = 'Morning'): Promise<WorkforceDeficitResponse> => {
  const { data } = await apiClient.get<WorkforceDeficitResponse>('/workforce/deficits', {
    params: { shift },
  });
  return data;
};

export const fetchRoster = async (shift?: string): Promise<RosterAssignment[]> => {
  const { data } = await apiClient.get<RosterAssignment[]>('/workforce/roster', {
    params: shift && shift !== 'ALL' ? { shift } : {},
  });
  return data;
};

export const updateStaffStatus = async (
  assignmentId: string,
  status: string,
  isOnDuty?: boolean
): Promise<RosterAssignment> => {
  const { data } = await apiClient.patch<RosterAssignment>(`/workforce/assignments/${assignmentId}/status`, {
    status,
    is_on_duty: isOnDuty,
  });
  return data;
};

// ==================== PHASE 3 APIS ====================

export const runBedAllocationOptimization = async (customPatients?: any[]): Promise<OptimizationResponse> => {
  const { data } = await apiClient.post<OptimizationResponse>(
    '/optimization/allocate-beds',
    customPatients || []
  );
  return data;
};

export const runScenarioSimulation = async (params: {
  arrival_surge_multiplier: number;
  nurse_absenteeism_pct: number;
  out_of_service_bed_pct: number;
  horizon_hours: number;
}): Promise<SimulationResponse> => {
  const { data } = await apiClient.post<SimulationResponse>(
    '/optimization/simulate-scenario',
    params
  );
  return data;
};

export const fetchCrisisTemplates = async (): Promise<CrisisTemplate[]> => {
  const { data } = await apiClient.get<CrisisTemplate[]>('/optimization/crisis-templates');
  return data;
};

// ==================== PHASE 4: CARE CONTINUITY & SHAP APIS ====================

export const fetchContinuityOverview = async (limit: number = 100): Promise<ContinuityOverviewResponse> => {
  const { data } = await apiClient.get<ContinuityOverviewResponse>('/continuity/overview', {
    params: { limit },
  });
  return data;
};

export const fetchContinuityCohort = async (
  tier: string = 'ALL',
  limit: number = 50
): Promise<PatientCohortItem[]> => {
  const { data } = await apiClient.get<PatientCohortItem[]>('/continuity/cohort', {
    params: { tier, limit },
  });
  return data;
};

export const fetchPatientRiskExplanation = async (encounterId: string): Promise<PatientRiskEvaluation> => {
  const { data } = await apiClient.get<PatientRiskEvaluation>(`/continuity/patient/${encounterId}`);
  return data;
};

export const evaluateCustomPatientRisk = async (
  req: EvaluatePatientRequest
): Promise<PatientRiskEvaluation> => {
  const { data } = await apiClient.post<PatientRiskEvaluation>('/continuity/evaluate-patient', req);
  return data;
};

