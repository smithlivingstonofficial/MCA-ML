import React from 'react';
import { Activity, AlertTriangle, Users, BedDouble, ShieldAlert } from 'lucide-react';
import { ExecutiveTelemetry } from '../../types';

interface HeaderTelemetryProps {
  telemetry?: ExecutiveTelemetry;
  isLoading: boolean;
}

export const HeaderTelemetry: React.FC<HeaderTelemetryProps> = ({ telemetry, isLoading }) => {
  if (isLoading || !telemetry) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 animate-pulse">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="h-28 bg-slate-900 border border-slate-800 rounded-xl"></div>
        ))}
      </div>
    );
  }

  const occPct = (telemetry.staffed_occupancy_rate * 100).toFixed(1);
  const isHighOcc = telemetry.staffed_occupancy_rate >= 0.85;
  const isCriticalOcc = telemetry.staffed_occupancy_rate >= 0.95;

  return (
    <div className="space-y-4">
      {/* Top Banner with Alert Ticker */}
      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800/80 p-4 rounded-2xl backdrop-blur">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-sky-500/10 border border-sky-500/20 rounded-xl text-sky-400">
            <Activity className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-tight text-white">Hospital Operations Command Center</h1>
              <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
                LIVE
              </span>
            </div>
            <p className="text-xs text-slate-400">Integrated Decision Support & Usable Capacity Telemetry</p>
          </div>
        </div>

        {/* Data Source Notice */}
        <div className="flex items-center gap-2 bg-slate-800/60 px-3 py-1.5 rounded-lg border border-slate-700/50 text-xs text-slate-300">
          <span className="w-2 h-2 rounded-full bg-amber-400"></span>
          <span>Verified Synthetic Demo Baseline (Seed 42)</span>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        {/* Card 1: Total Census */}
        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Active Census</span>
            <Users className="w-4 h-4 text-sky-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">{telemetry.total_census}</span>
            <span className="text-xs text-slate-500">/ {telemetry.total_physical_beds} beds</span>
          </div>
          <div className="mt-2 text-xs text-slate-400">Hospital-wide admitted count</div>
        </div>

        {/* Card 2: Staffed Occupancy */}
        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Staffed Occupancy</span>
            <BedDouble className={`w-4 h-4 ${isCriticalOcc ? 'text-rose-400' : isHighOcc ? 'text-amber-400' : 'text-emerald-400'}`} />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className={`text-3xl font-extrabold ${isCriticalOcc ? 'text-rose-400' : isHighOcc ? 'text-amber-400' : 'text-emerald-400'}`}>
              {occPct}%
            </span>
            <span className="text-xs text-slate-500">ceiling {telemetry.total_staffed_beds}</span>
          </div>
          <div className="mt-2 w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full ${isCriticalOcc ? 'bg-rose-500' : isHighOcc ? 'bg-amber-500' : 'bg-emerald-500'}`}
              style={{ width: `${Math.min(100, Number(occPct))}%` }}
            ></div>
          </div>
        </div>

        {/* Card 3: ED Arrivals 24h */}
        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">ED Inflow (24h)</span>
            <Activity className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">{telemetry.ed_arrivals_last_24h}</span>
            <span className="text-xs text-indigo-400 font-medium">observed</span>
          </div>
          <div className="mt-2 text-xs text-slate-400">Emergency admissions</div>
        </div>

        {/* Card 4: Forecast 24h */}
        <div className="bg-slate-900/80 border border-slate-800 p-4 rounded-xl relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">24h Forecast</span>
            <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-sky-500/10 text-sky-400 border border-sky-500/20">GBDT</span>
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-sky-400">{telemetry.ed_forecast_next_24h}</span>
            <span className="text-xs text-slate-500">patients</span>
          </div>
          <div className="mt-2 text-xs text-slate-400">
            {telemetry.overcrowding_alert ? (
              <span className="text-rose-400 font-medium">Overcrowding alert active</span>
            ) : (
              <span className="text-emerald-400">Within nominal bounds</span>
            )}
          </div>
        </div>

        {/* Card 5: Operational Alerts */}
        <div className={`p-4 rounded-xl border relative overflow-hidden ${
          telemetry.active_alerts.length > 0
            ? 'bg-rose-950/20 border-rose-800/60'
            : 'bg-slate-900/80 border-slate-800'
        }`}>
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">Active Alerts</span>
            {telemetry.active_alerts.length > 0 ? (
              <ShieldAlert className="w-4 h-4 text-rose-400 animate-bounce" />
            ) : (
              <AlertTriangle className="w-4 h-4 text-slate-500" />
            )}
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className={`text-3xl font-extrabold ${telemetry.active_alerts.length > 0 ? 'text-rose-400' : 'text-slate-400'}`}>
              {telemetry.active_alerts.length}
            </span>
            <span className="text-xs text-slate-500">triggers</span>
          </div>
          <div className="mt-2 text-xs text-slate-400">
            {telemetry.active_alerts.length > 0 ? 'Capacity & staff alerts' : 'All wards nominal'}
          </div>
        </div>
      </div>
    </div>
  );
};

