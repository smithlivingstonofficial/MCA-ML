import React, { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import {
  Cpu,
  Sliders,
  CheckCircle2,
  AlertOctagon,
  ShieldAlert,
  Flame,
  ArrowRight,
  TrendingUp,
  RotateCcw,
  Sparkles
} from 'lucide-react';
import {
  runBedAllocationOptimization,
  runScenarioSimulation,
  fetchCrisisTemplates
} from '../services/api';
import { CrisisTemplate } from '../types';

export const OptimizationPage: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = useState<'SOLVER' | 'SIMULATOR'>('SOLVER');

  // Simulator Sliders State
  const [surgeMultiplier, setSurgeMultiplier] = useState<number>(1.4);
  const [absenteeismPct, setAbsenteeismPct] = useState<number>(0.15);
  const [outOfServicePct, setOutOfServicePct] = useState<number>(0.05);
  const simHorizon = 24;

  // Queries
  const { data: crisisTemplates } = useQuery({
    queryKey: ['crisis-templates'],
    queryFn: fetchCrisisTemplates,
  });

  // PuLP Solver Mutation
  const solverMutation = useMutation({
    mutationFn: () => runBedAllocationOptimization(),
  });

  // Simulator Mutation
  const simMutation = useMutation({
    mutationFn: () =>
      runScenarioSimulation({
        arrival_surge_multiplier: surgeMultiplier,
        nurse_absenteeism_pct: absenteeismPct,
        out_of_service_bed_pct: outOfServicePct,
        horizon_hours: simHorizon,
      }),
  });

  const applyTemplate = (tpl: CrisisTemplate) => {
    setSurgeMultiplier(tpl.arrival_surge_multiplier);
    setAbsenteeismPct(tpl.nurse_absenteeism_pct);
    setOutOfServicePct(tpl.out_of_service_bed_pct);
    simMutation.mutate();
  };

  const solverData = solverMutation.data;
  const simData = simMutation.data;

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header and Sub-Tab Switcher */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-4 rounded-2xl backdrop-blur">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Cpu className="w-5 h-5 text-sky-400" />
            Module 5: Mathematical Optimization & Surge Simulation
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            PuLP Mixed-Integer Linear Programming (MILP) with HiGHS Solver + What-If Crisis Simulator
          </p>
        </div>

        <div className="flex items-center gap-1.5 bg-slate-950 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveSubTab('SOLVER')}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
              activeSubTab === 'SOLVER'
                ? 'bg-sky-500 text-slate-950 shadow-sm'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            PuLP Bed Allocator
          </button>
          <button
            onClick={() => {
              setActiveSubTab('SIMULATOR');
              if (!simData) simMutation.mutate();
            }}
            className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-all ${
              activeSubTab === 'SIMULATOR'
                ? 'bg-indigo-500 text-white shadow-sm'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            What-If Scenario Simulator
          </button>
        </div>
      </div>

      {/* ==================== 1. PuLP MILP SOLVER TAB ==================== */}
      {activeSubTab === 'SOLVER' && (
        <div className="space-y-6">
          {/* Solver Control Bar */}
          <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <span className="text-sm font-bold text-white">Dynamic Acuity Bed Allocation</span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-sky-500/10 text-sky-400 border border-sky-500/20 font-mono">
                  MILP • HiGHS Engine
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Solves optimal patient-to-bed matching enforcing ICU acuity rules, isolation compliance, and staffed nurse ceilings.
              </p>
            </div>

            <button
              onClick={() => solverMutation.mutate()}
              disabled={solverMutation.isPending}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-sky-500 to-indigo-500 text-slate-950 font-bold text-xs hover:opacity-90 transition-all shadow-lg shadow-sky-500/20 flex items-center gap-2"
            >
              <Cpu className={`w-4 h-4 ${solverMutation.isPending ? 'animate-spin' : ''}`} />
              <span>{solverMutation.isPending ? 'Solving MILP Problem...' : 'Run PuLP MILP Solver'}</span>
            </button>
          </div>

          {/* Solver Output Results */}
          {solverData && (
            <div className="space-y-6">
              {/* Status Header */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
                <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400">Solver Status</div>
                  <div className={`text-xl font-extrabold mt-1 ${
                    solverData.status === 'Optimal' ? 'text-emerald-400' : 'text-amber-400'
                  }`}>
                    {solverData.status}
                  </div>
                </div>
                <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl">
                  <div className="text-xs text-slate-400">Execution Speed</div>
                  <div className="text-xl font-extrabold text-white mt-1">
                    {solverData.execution_time_ms} ms
                  </div>
                </div>
                <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl">
                  <div className="text-xs text-emerald-400">Assigned Patients</div>
                  <div className="text-xl font-extrabold text-emerald-400 mt-1">
                    {solverData.assigned_count} / {solverData.total_patients}
                  </div>
                </div>
                <div className="p-4 bg-slate-900/80 border border-slate-800 rounded-xl">
                  <div className="text-xs text-rose-400">Unassigned Demand</div>
                  <div className="text-xl font-extrabold text-rose-400 mt-1">
                    {solverData.unassigned_count}
                  </div>
                </div>
              </div>

              {/* Infeasibility / Constraint Bottleneck Diagnostics */}
              {solverData.diagnostics && solverData.diagnostics.length > 0 && (
                <div className="p-4 bg-amber-500/10 border border-amber-500/30 rounded-xl space-y-2 text-xs text-amber-300">
                  <div className="flex items-center gap-2 font-bold text-sm text-amber-400">
                    <AlertOctagon className="w-4 h-4 flex-shrink-0" />
                    <span>Hard Clinical Constraint Protection Triggered:</span>
                  </div>
                  <ul className="list-disc list-inside space-y-1 pl-2 text-slate-300">
                    {solverData.diagnostics.map((diag, idx) => (
                      <li key={idx}>{diag}</li>
                    ))}
                  </ul>
                  <p className="text-[11px] text-slate-400 italic pt-1">
                    Notice: PuLP never relaxes patient safety rules or nurse capacity ceilings to force an assignment.
                  </p>
                </div>
              )}

              {/* Assignments Table */}
              <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-bold text-white text-sm">Optimal Bed Allocation Schedule</h3>
                  <span className="text-xs text-emerald-400 font-semibold flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    All Hard Constraints Satisfied
                  </span>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px]">
                        <th className="py-2.5 px-4">Patient Reference</th>
                        <th className="py-2.5 px-4">Acuity</th>
                        <th className="py-2.5 px-4">Allocated Bed</th>
                        <th className="py-2.5 px-4">Ward / Unit</th>
                        <th className="py-2.5 px-4">Specialty</th>
                        <th className="py-2.5 px-4 text-right">Compliance Badges</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/40">
                      {solverData.assignments.map((alloc) => (
                        <tr key={alloc.patient_id} className="hover:bg-slate-800/30">
                          <td className="py-2.5 px-4 font-mono font-bold text-white">
                            {alloc.patient_anon_id}
                          </td>
                          <td className="py-2.5 px-4">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              alloc.esi_score <= 2 ? 'bg-rose-500/20 text-rose-400' : 'bg-sky-500/20 text-sky-400'
                            }`}>
                              ESI {alloc.esi_score}
                            </span>
                          </td>
                          <td className="py-2.5 px-4 font-bold text-sky-400">
                            {alloc.bed_number}
                          </td>
                          <td className="py-2.5 px-4 text-slate-300 font-medium">
                            {alloc.ward_name}
                          </td>
                          <td className="py-2.5 px-4 text-slate-400">
                            {alloc.specialty}
                          </td>
                          <td className="py-2.5 px-4 text-right space-x-1">
                            {alloc.is_isolation_certified && (
                              <span className="px-1.5 py-0.5 rounded text-[9px] bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                                Isolation Certified
                              </span>
                            )}
                            <span className="px-1.5 py-0.5 rounded text-[9px] bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                              Nurse Ratio OK
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {!solverData && (
            <div className="p-12 bg-slate-900/40 border border-slate-800/60 rounded-2xl text-center space-y-3">
              <Sparkles className="w-8 h-8 text-sky-400 mx-auto animate-bounce" />
              <p className="text-base font-bold text-white">PuLP MILP Solver Ready</p>
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                Click "Run PuLP MILP Solver" above to evaluate real-time queue conditions against current usable bed capacity and nursing ratios.
              </p>
            </div>
          )}
        </div>
      )}

      {/* ==================== 2. WHAT-IF SCENARIO SIMULATOR TAB ==================== */}
      {activeSubTab === 'SIMULATOR' && (
        <div className="space-y-6">
          {/* Preset Crisis Templates */}
          <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-4">
            <div className="flex items-center gap-2">
              <Flame className="w-5 h-5 text-amber-400" />
              <h2 className="text-base font-bold text-white">Standard Crisis & Surge Templates</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {crisisTemplates?.map((tpl) => (
                <button
                  key={tpl.template_key}
                  onClick={() => applyTemplate(tpl)}
                  className="p-4 bg-slate-950/60 hover:bg-slate-800/40 border border-slate-800 rounded-xl text-left space-y-2 transition-all hover:scale-[1.02]"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-sm text-white">{tpl.name}</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
                      {tpl.arrival_surge_multiplier}x
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">{tpl.description}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Interactive Sliders Panel */}
          <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sliders className="w-5 h-5 text-indigo-400" />
                <h2 className="text-base font-bold text-white">Interactive Operational Sliders</h2>
              </div>
              <button
                onClick={() => simMutation.mutate()}
                disabled={simMutation.isPending}
                className="px-4 py-2 rounded-xl bg-indigo-500 hover:bg-indigo-400 text-white font-bold text-xs transition-all shadow-md flex items-center gap-1.5"
              >
                <RotateCcw className={`w-3.5 h-3.5 ${simMutation.isPending ? 'animate-spin' : ''}`} />
                <span>Simulate Scenario</span>
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 text-xs">
              {/* Slider 1: Arrival Surge */}
              <div className="space-y-2 p-4 bg-slate-950/60 rounded-xl border border-slate-800/80">
                <div className="flex justify-between font-medium">
                  <span className="text-slate-300">Arrival Surge Multiplier:</span>
                  <span className="font-bold text-sky-400">{surgeMultiplier.toFixed(2)}x (+{Math.round((surgeMultiplier - 1) * 100)}%)</span>
                </div>
                <input
                  type="range"
                  min="0.8"
                  max="2.5"
                  step="0.05"
                  value={surgeMultiplier}
                  onChange={(e) => setSurgeMultiplier(parseFloat(e.target.value))}
                  className="w-full accent-sky-400"
                />
              </div>

              {/* Slider 2: Nurse Absenteeism */}
              <div className="space-y-2 p-4 bg-slate-950/60 rounded-xl border border-slate-800/80">
                <div className="flex justify-between font-medium">
                  <span className="text-slate-300">Staff Absenteeism:</span>
                  <span className="font-bold text-amber-400">{Math.round(absenteeismPct * 100)}% absent</span>
                </div>
                <input
                  type="range"
                  min="0.0"
                  max="0.5"
                  step="0.05"
                  value={absenteeismPct}
                  onChange={(e) => setAbsenteeismPct(parseFloat(e.target.value))}
                  className="w-full accent-amber-400"
                />
              </div>

              {/* Slider 3: Out of Service Beds */}
              <div className="space-y-2 p-4 bg-slate-950/60 rounded-xl border border-slate-800/80">
                <div className="flex justify-between font-medium">
                  <span className="text-slate-300">Out-of-Service Beds:</span>
                  <span className="font-bold text-rose-400">{Math.round(outOfServicePct * 100)}% offline</span>
                </div>
                <input
                  type="range"
                  min="0.0"
                  max="0.3"
                  step="0.05"
                  value={outOfServicePct}
                  onChange={(e) => setOutOfServicePct(parseFloat(e.target.value))}
                  className="w-full accent-rose-400"
                />
              </div>
            </div>
          </div>

          {/* Comparative KPI Matrix */}
          {simData && (
            <div className="space-y-6">
              <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-bold text-white text-sm">Baseline vs. Simulated Crisis Outcomes</h3>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-400">Hospital Stress Index:</span>
                    <span className={`text-sm font-extrabold px-2.5 py-0.5 rounded-full border ${
                      (simData.simulated.hospital_stress_index ?? 0) >= 90
                        ? 'bg-rose-500/20 text-rose-400 border-rose-500/40'
                        : 'bg-amber-500/20 text-amber-400 border-amber-500/40'
                    }`}>
                      {simData.simulated.hospital_stress_index}%
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
                  <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl space-y-2">
                    <div className="text-xs text-slate-400">24h Emergency Inflow</div>
                    <div className="flex items-center justify-center gap-2">
                      <span className="text-base text-slate-400 font-semibold">{simData.baseline.arrivals_24h}</span>
                      <ArrowRight className="w-3.5 h-3.5 text-sky-400" />
                      <span className="text-2xl font-extrabold text-sky-400">{simData.simulated.arrivals_24h}</span>
                    </div>
                  </div>

                  <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl space-y-2">
                    <div className="text-xs text-slate-400">Usable Staffed Capacity</div>
                    <div className="flex items-center justify-center gap-2">
                      <span className="text-base text-slate-400 font-semibold">{simData.baseline.total_staffed_capacity}</span>
                      <ArrowRight className="w-3.5 h-3.5 text-amber-400" />
                      <span className="text-2xl font-extrabold text-amber-400">{simData.simulated.total_staffed_capacity}</span>
                    </div>
                  </div>

                  <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl space-y-2">
                    <div className="text-xs text-slate-400">Staffed Occupancy Rate</div>
                    <div className="flex items-center justify-center gap-2">
                      <span className="text-base text-slate-400 font-semibold">{simData.baseline.staffed_occupancy_pct}%</span>
                      <ArrowRight className="w-3.5 h-3.5 text-rose-400" />
                      <span className="text-2xl font-extrabold text-rose-400">{simData.simulated.staffed_occupancy_pct}%</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Actionable AI Recommendations */}
              {simData.recommendations.length > 0 && (
                <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-3">
                  <div className="flex items-center gap-2 text-amber-400 font-bold text-sm">
                    <ShieldAlert className="w-4 h-4" />
                    <span>Operational Mitigations & Crisis Response Plan</span>
                  </div>
                  <div className="space-y-2 text-xs text-slate-300">
                    {simData.recommendations.map((rec, idx) => (
                      <div key={idx} className="p-3 bg-slate-950/60 rounded-xl border border-slate-800 flex items-start gap-2">
                        <TrendingUp className="w-3.5 h-3.5 text-sky-400 flex-shrink-0 mt-0.5" />
                        <span>{rec}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
