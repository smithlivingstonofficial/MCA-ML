import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { RefreshCw, ShieldCheck } from 'lucide-react';
import {
  fetchTelemetryOverview,
  fetchWardCapacities,
  fetchBeds,
  updateBedState,
  fetchArrivalForecast
} from '../services/api';
import { HeaderTelemetry } from '../components/telemetry/HeaderTelemetry';
import { ForecastChart } from '../components/charts/ForecastChart';
import { AlertsPanel } from '../components/telemetry/AlertsPanel';
import { BedMatrix } from '../components/beds/BedMatrix';
import { BedState } from '../types';

export const OverviewDashboard: React.FC = () => {
  const queryClient = useQueryClient();
  const [horizon, setHorizon] = useState<number>(24);

  // Queries
  const { data: telemetry, isLoading: loadingTelemetry, refetch: refetchTelemetry } = useQuery({
    queryKey: ['telemetry'],
    queryFn: fetchTelemetryOverview,
    refetchInterval: 30000,
  });

  const { data: wards, isLoading: loadingWards, refetch: refetchWards } = useQuery({
    queryKey: ['wards'],
    queryFn: fetchWardCapacities,
    refetchInterval: 30000,
  });

  const { data: beds, isLoading: loadingBeds, refetch: refetchBeds } = useQuery({
    queryKey: ['beds'],
    queryFn: () => fetchBeds(),
    refetchInterval: 30000,
  });

  const { data: forecast, isLoading: loadingForecast, refetch: refetchForecast } = useQuery({
    queryKey: ['forecast', horizon],
    queryFn: () => fetchArrivalForecast(horizon),
    refetchInterval: 60000,
  });

  // Bed state transition mutation
  const bedStateMutation = useMutation({
    mutationFn: ({ bedId, newState, reason }: { bedId: string; newState: BedState; reason?: string }) =>
      updateBedState(bedId, newState, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['beds'] });
      queryClient.invalidateQueries({ queryKey: ['wards'] });
      queryClient.invalidateQueries({ queryKey: ['telemetry'] });
    },
  });

  const handleStateChange = async (bedId: string, newState: BedState, reason?: string) => {
    await bedStateMutation.mutateAsync({ bedId, newState, reason });
  };

  const handleRefreshAll = () => {
    refetchTelemetry();
    refetchWards();
    refetchBeds();
    refetchForecast();
  };

  const isRefreshing = loadingTelemetry || loadingWards || loadingBeds || loadingForecast;

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Top Header Actions */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>Operational Minimum Viable Product (Phase 1 Baseline)</span>
        </div>

        <button
          onClick={handleRefreshAll}
          disabled={isRefreshing}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-700/80 rounded-xl text-xs font-semibold text-slate-200 transition-all shadow-sm"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-sky-400' : ''}`} />
          <span>{isRefreshing ? 'Syncing...' : 'Refresh Telemetry'}</span>
        </button>
      </div>

      {/* 1. Header Telemetry KPIs */}
      <HeaderTelemetry telemetry={telemetry} isLoading={loadingTelemetry} />

      {/* 2. Middle Row: Forecast & Alerts Inbox */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ForecastChart
            forecastData={forecast}
            isLoading={loadingForecast}
            onHorizonChange={setHorizon}
            currentHorizon={horizon}
          />
        </div>
        <div className="lg:col-span-1">
          <AlertsPanel alerts={telemetry?.active_alerts || []} />
        </div>
      </div>

      {/* 3. Operational Bed Matrix Grid */}
      <BedMatrix
        wards={wards || []}
        beds={beds || []}
        isLoading={loadingWards || loadingBeds}
        onStateChange={handleStateChange}
      />
    </div>
  );
};

