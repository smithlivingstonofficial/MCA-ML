import axios from 'axios';
import {
  ExecutiveTelemetry,
  WardCapacitySummary,
  Bed,
  ArrivalForecastResponse,
  BedState
} from '../types';

const API_BASE = '/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

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

