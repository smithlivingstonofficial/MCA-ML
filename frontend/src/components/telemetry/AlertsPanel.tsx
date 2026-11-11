import React from 'react';
import { AlertTriangle, ShieldAlert, CheckCircle2, Bell } from 'lucide-react';
import { ActiveAlert } from '../../types';

interface AlertsPanelProps {
  alerts: ActiveAlert[];
}

export const AlertsPanel: React.FC<AlertsPanelProps> = ({ alerts }) => {
  return (
    <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bell className="w-5 h-5 text-amber-400" />
          <h2 className="text-base font-bold text-white">Module 7: Prioritized Operations Alert Inbox</h2>
        </div>
        <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300">
          {alerts.length} Active Triggers
        </span>
      </div>

      {alerts.length === 0 ? (
        <div className="p-6 bg-slate-950/40 rounded-xl border border-slate-800/60 text-center space-y-2">
          <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto" />
          <p className="text-sm font-semibold text-white">All Units Operational & Balanced</p>
          <p className="text-xs text-slate-400">No severe staffing deficits or capacity bottlenecks detected.</p>
        </div>
      ) : (
        <div className="space-y-2.5 max-h-72 overflow-y-auto pr-1">
          {alerts.map((alert, idx) => {
            const isCritical = alert.severity === 'CRITICAL';
            return (
              <div
                key={idx}
                className={`p-3.5 rounded-xl border flex items-start gap-3 transition-all ${
                  isCritical
                    ? 'bg-rose-950/30 border-rose-800/60 text-rose-200'
                    : 'bg-amber-950/20 border-amber-800/50 text-amber-200'
                }`}
              >
                {isCritical ? (
                  <ShieldAlert className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
                ) : (
                  <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
                )}
                <div className="space-y-0.5">
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-[10px] font-bold px-1.5 py-0.5 rounded uppercase tracking-wider ${
                        isCritical ? 'bg-rose-500/20 text-rose-400' : 'bg-amber-500/20 text-amber-400'
                      }`}
                    >
                      {alert.severity}
                    </span>
                    <span className="text-xs font-bold text-white">[{alert.ward_code}]</span>
                  </div>
                  <p className="text-xs leading-relaxed">{alert.message}</p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

