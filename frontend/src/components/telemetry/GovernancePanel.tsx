import React from 'react';
import { ShieldCheck, Activity, Database, GitBranch, AlertCircle, CheckCircle } from 'lucide-react';
import { ModelGovernanceResponse } from '../../types';

interface GovernancePanelProps {
  governance: ModelGovernanceResponse | null;
  isLoading: boolean;
}

export const GovernancePanel: React.FC<GovernancePanelProps> = ({ governance, isLoading }) => {
  if (isLoading) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 text-center text-slate-500 text-xs">
        Loading Model Governance & Data Drift telemetry...
      </div>
    );
  }

  if (!governance) return null;

  const isStable = governance.overall_governance_status === 'STABLE';
  const isModerate = governance.overall_governance_status === 'MODERATE_DRIFT';

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 space-y-6 shadow-xl">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-400">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white">
              Module 7: Model Governance, Drift Detection & Quality Assurance
            </h2>
            <p className="text-xs text-slate-400">
              Automated Population Stability Index (PSI), Kolmogorov-Smirnov tests, and pipeline integrity checks
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span
            className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider flex items-center gap-1.5 ${
              isStable
                ? 'bg-emerald-950/80 text-emerald-300 border border-emerald-800'
                : isModerate
                ? 'bg-amber-950/80 text-amber-300 border border-amber-800'
                : 'bg-rose-950/80 text-rose-300 border border-rose-800'
            }`}
          >
            <span
              className={`w-2 h-2 rounded-full ${
                isStable ? 'bg-emerald-400' : isModerate ? 'bg-amber-400' : 'bg-rose-400 animate-ping'
              }`}
            />
            {governance.overall_governance_status}
          </span>
        </div>
      </div>

      {/* Grid: 3 Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Section 1: Feature Drift Metrics (PSI & KS) */}
        <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-4 space-y-3">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-300 uppercase tracking-wider">
            <Activity className="w-4 h-4 text-sky-400" />
            <span>Feature Drift Diagnostics</span>
          </div>

          <div className="space-y-2.5">
            {Object.entries(governance.features).map(([key, f]) => {
              const label =
                key === 'hourly_arrivals'
                  ? 'Hourly ED Arrivals'
                  : key === 'length_of_stay'
                  ? 'Length of Stay (LOS)'
                  : 'Triage Acuity (ESI)';

              return (
                <div key={key} className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800/80 space-y-1">
                  <div className="flex justify-between items-center text-xs">
                    <span className="font-semibold text-slate-200">{label}</span>
                    <span
                      className={`text-[10px] font-mono font-bold px-1.5 py-0.5 rounded ${
                        f.status === 'STABLE'
                          ? 'bg-emerald-950 text-emerald-400'
                          : 'bg-amber-950 text-amber-400'
                      }`}
                    >
                      PSI: {f.psi.toFixed(4)}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono">
                    <span>KS stat: {f.ks_statistic.toFixed(3)}</span>
                    <span>p-val: {f.ks_p_value.toFixed(4)}</span>
                    <span className={f.drift_detected ? 'text-amber-400' : 'text-emerald-400'}>
                      {f.drift_detected ? 'Shift Detected' : 'Aligned'}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Section 2: Data Quality & Pipeline Integrity */}
        <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-4 space-y-3">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-300 uppercase tracking-wider">
            <Database className="w-4 h-4 text-emerald-400" />
            <span>Data Quality Audit</span>
          </div>

          <div className="space-y-3">
            <div className="bg-slate-900/80 p-3 rounded-lg border border-slate-800 flex items-center justify-between">
              <div>
                <p className="text-xs text-slate-400">Quality Score</p>
                <p className="text-2xl font-bold text-emerald-400 font-mono">
                  {governance.data_quality.quality_score_pct.toFixed(1)}%
                </p>
              </div>
              <div className="text-right">
                <p className="text-xs text-slate-400">Records Audited</p>
                <p className="text-lg font-bold text-white font-mono">
                  {governance.data_quality.records_audited}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="bg-slate-900/60 p-2 rounded border border-slate-800">
                <p className="text-[11px] text-slate-400">Timestamp Anomalies</p>
                <p className="font-mono font-bold text-slate-200 mt-0.5">
                  {governance.data_quality.timestamp_anomalies}
                </p>
              </div>
              <div className="bg-slate-900/60 p-2 rounded border border-slate-800">
                <p className="text-[11px] text-slate-400">Range Anomalies</p>
                <p className="font-mono font-bold text-slate-200 mt-0.5">
                  {governance.data_quality.range_anomalies}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2 text-xs text-emerald-400 bg-emerald-950/20 p-2 rounded border border-emerald-900/30">
              <CheckCircle className="w-4 h-4 flex-shrink-0" />
              <span>Timestamp ordering & ESI range bounds valid.</span>
            </div>
          </div>
        </div>

        {/* Section 3: Active Model Registry */}
        <div className="bg-slate-950/60 border border-slate-800 rounded-xl p-4 space-y-3">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-300 uppercase tracking-wider">
            <GitBranch className="w-4 h-4 text-purple-400" />
            <span>Active Model Registry</span>
          </div>

          <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
            {governance.active_models.map((m, idx) => (
              <div key={idx} className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800 text-xs space-y-1">
                <div className="flex justify-between items-center">
                  <span className="font-semibold text-white">{m.model_name}</span>
                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                    v{m.version}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 truncate">{m.architecture}</p>
                <div className="flex items-center justify-between text-[10px] text-purple-300 font-mono pt-0.5">
                  <span>
                    {m.validation_wape
                      ? `WAPE: ${(m.validation_wape * 100).toFixed(1)}%`
                      : m.validation_roc_auc
                      ? `ROC-AUC: ${m.validation_roc_auc.toFixed(3)}`
                      : 'HiGHS MILP'}
                  </span>
                  <span className="text-emerald-400 font-bold">{m.status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Advisory Banner */}
      <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800 flex items-center gap-3 text-xs text-slate-300">
        <AlertCircle className="w-4 h-4 text-sky-400 flex-shrink-0" />
        <span>
          <strong className="text-white">Governance Directive:</strong> {governance.recommendation}
        </span>
      </div>
    </div>
  );
};
