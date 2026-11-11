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
  RosterAssignment
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
