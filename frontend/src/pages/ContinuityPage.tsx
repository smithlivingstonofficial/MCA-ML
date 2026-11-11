import React, { useState, useEffect } from 'react';
import {
  fetchContinuityOverview,
  fetchContinuityCohort,
  fetchPatientRiskExplanation,
  evaluateCustomPatientRisk
} from '../services/api';
import {
  ContinuityOverviewResponse,
  PatientCohortItem,
  PatientRiskEvaluation,
  EvaluatePatientRequest
} from '../types';

export const ContinuityPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'cohort' | 'simulator'>('cohort');
  const [overview, setOverview] = useState<ContinuityOverviewResponse | null>(null);
  const [cohort, setCohort] = useState<PatientCohortItem[]>([]);
  const [tierFilter, setTierFilter] = useState<string>('ALL');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [selectedPatientId, setSelectedPatientId] = useState<string | null>(null);
  const [activeExplanation, setActiveExplanation] = useState<PatientRiskEvaluation | null>(null);
  const [isExplaining, setIsExplaining] = useState<boolean>(false);

  // Custom Simulator State
  const [simAge, setSimAge] = useState<number>(72);
  const [simEsi, setSimEsi] = useState<number>(2);
  const [simLos, setSimLos] = useState<number>(72);
  const [simPriors, setSimPriors] = useState<number>(3);
  const [simComorb, setSimComorb] = useState<number>(3);
  const [simIsEmerg, setSimIsEmerg] = useState<boolean>(true);
  const [simDischargeHome, setSimDischargeHome] = useState<boolean>(true);
  const [simComplaint, setSimComplaint] = useState<string>('Severe shortness of breath and congestive symptoms');
  const [simResult, setSimResult] = useState<PatientRiskEvaluation | null>(null);
  const [isSimulating, setIsSimulating] = useState<boolean>(false);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [ovData, cohData] = await Promise.all([
        fetchContinuityOverview(100),
        fetchContinuityCohort(tierFilter, 50)
      ]);
      setOverview(ovData);
      setCohort(cohData);
    } catch (err) {
      console.error('Failed to load continuity data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [tierFilter]);

  const handleSelectPatient = async (encounterId: string) => {
    setSelectedPatientId(encounterId);
    setIsExplaining(true);
    try {
      const explanation = await fetchPatientRiskExplanation(encounterId);
      setActiveExplanation(explanation);
    } catch (err) {
      console.error('Failed to fetch patient explanation:', err);
    } finally {
      setIsExplaining(false);
    }
  };

  const handleRunSimulation = async () => {
    setIsSimulating(true);
    try {
      const payload: EvaluatePatientRequest = {
        encounter_id: `SIM-ENC-${Date.now().toString().slice(-4)}`,
        patient_mrn: 'MRN-SIMULATED-01',
        department: 'Cardiology / Acute Care',
        age: simAge,
        esi_score: simEsi,
        actual_los_hours: simLos,
        prior_admissions_count: simPriors,
        comorbidity_count: simComorb,
        encounter_type: simIsEmerg ? 'Emergency' : 'Elective',
        disposition: simDischargeHome ? 'Home' : 'Facility',
        chief_complaint: simComplaint
      };

      const res = await evaluateCustomPatientRisk(payload);
      setSimResult(res);
    } catch (err) {
      console.error('Simulation error:', err);
    } finally {
      setIsSimulating(false);
    }
  };

  // Run initial simulation on tab mount if null
  useEffect(() => {
    if (activeTab === 'simulator' && !simResult) {
      handleRunSimulation();
    }
  }, [activeTab]);

  const filteredCohort = cohort.filter((p) => {
    const matchesSearch =
      p.patient_mrn.toLowerCase().includes(searchTerm.toLowerCase()) ||
      p.department.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  return (
    <div className="space-y-6">
      {/* Governance & Disclaimer Banner */}
      <div className="bg-slate-800/80 border-l-4 border-amber-500 rounded-r-lg p-4 text-xs text-slate-300 flex items-start justify-between shadow-lg">
        <div className="space-y-1">
          <div className="flex items-center gap-2 font-bold text-amber-400 text-sm">
            <span>🛡️</span>
            <span>Module 6 Governance & Clinical Safety Protocol</span>
          </div>
          <p>
            Machine learning predictions (HistGBDT + TreeSHAP) are decision-support signals only. They are{' '}
            <strong className="text-white">never</strong> used to deny admissions, triage levels, or withhold care.
            Risk scores identify post-acute patients who may benefit from barrier-reduction calls and proactive medication therapy management.
          </p>
        </div>
        <div className="hidden md:flex items-center gap-2 bg-slate-900/80 px-3 py-1.5 rounded border border-slate-700 text-slate-400 font-mono text-[11px]">
          <span>Model: HistGBDT</span>
          <span>•</span>
          <span>SHAP: TreeExplainer</span>
        </div>
      </div>

      {/* Cohort Overview Metrics */}
      {overview && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4">
            <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">Cohort Evaluated</p>
            <p className="text-2xl font-bold text-white mt-1">{overview.total_cohort_evaluated}</p>
            <p className="text-[11px] text-slate-500 mt-0.5">Discharged patients</p>
          </div>

          <div className="bg-slate-900 border border-rose-900/40 rounded-xl p-4 relative overflow-hidden">
            <div className="absolute top-2 right-2 flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-rose-500"></span>
            </div>
            <p className="text-xs font-medium text-rose-400 uppercase tracking-wider">High Risk (&gt;35%)</p>
            <p className="text-2xl font-bold text-rose-400 mt-1">{overview.high_risk_count}</p>
            <p className="text-[11px] text-rose-400/70 mt-0.5">Priority outreach candidates</p>
          </div>

          <div className="bg-slate-900 border border-amber-900/40 rounded-xl p-4">
            <p className="text-xs font-medium text-amber-400 uppercase tracking-wider">Moderate Risk</p>
            <p className="text-2xl font-bold text-amber-400 mt-1">{overview.moderate_risk_count}</p>
            <p className="text-[11px] text-amber-400/70 mt-0.5">Standard transition follow-up</p>
          </div>

          <div className="bg-slate-900 border border-emerald-900/40 rounded-xl p-4">
            <p className="text-xs font-medium text-emerald-400 uppercase tracking-wider">Low Risk</p>
            <p className="text-2xl font-bold text-emerald-400 mt-1">{overview.low_risk_count}</p>
            <p className="text-[11px] text-emerald-400/70 mt-0.5">Routine discharge care</p>
          </div>

          <div className="bg-slate-900 border border-indigo-900/40 rounded-xl p-4 col-span-2 md:col-span-1">
            <p className="text-xs font-medium text-indigo-400 uppercase tracking-wider">Mean Readmit Risk</p>
            <p className="text-2xl font-bold text-indigo-400 mt-1">
              {(overview.mean_readmission_risk * 100).toFixed(1)}%
            </p>
            <p className="text-[11px] text-indigo-400/70 mt-0.5">Cohort baseline</p>
          </div>
        </div>
      )}

      {/* Tab Navigation */}
      <div className="flex border-b border-slate-800 gap-4">
        <button
          onClick={() => setActiveTab('cohort')}
          className={`pb-3 text-sm font-semibold transition-colors relative ${
            activeTab === 'cohort' ? 'text-indigo-400 border-b-2 border-indigo-500' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          📋 Post-Discharge Patient Cohort
        </button>
        <button
          onClick={() => setActiveTab('simulator')}
          className={`pb-3 text-sm font-semibold transition-colors relative ${
            activeTab === 'simulator' ? 'text-indigo-400 border-b-2 border-indigo-500' : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          🔬 Interactive TreeSHAP Risk Simulator
        </button>
      </div>

      {/* Tab 1: Cohort View */}
      {activeTab === 'cohort' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Cohort List */}
          <div className="lg:col-span-2 space-y-4">
            {/* Filter and Search Bar */}
            <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-slate-900 p-3 rounded-xl border border-slate-800">
              <div className="flex items-center gap-2 w-full sm:w-auto">
                <span className="text-xs text-slate-400">Risk Tier:</span>
                {['ALL', 'HIGH', 'MODERATE', 'LOW'].map((t) => (
                  <button
                    key={t}
                    onClick={() => setTierFilter(t)}
                    className={`px-2.5 py-1 text-xs rounded-lg font-medium transition-all ${
                      tierFilter === t
                        ? 'bg-indigo-600 text-white shadow-sm'
                        : 'bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-slate-200'
                    }`}
                  >
                    {t}
                  </button>
                ))}
              </div>
              <div className="w-full sm:w-64">
                <input
                  type="text"
                  placeholder="Search MRN or Dept..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-lg px-3 py-1.5 focus:outline-none focus:border-indigo-500"
                />
              </div>
            </div>

            {/* Patient Table */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-300">
                  <thead className="bg-slate-800/60 uppercase tracking-wider text-[11px] text-slate-400">
                    <tr>
                      <th className="py-3 px-4">Patient MRN</th>
                      <th className="py-3 px-4">Age</th>
                      <th className="py-3 px-4">Department</th>
                      <th className="py-3 px-4">LOS</th>
                      <th className="py-3 px-4">Readmit Risk</th>
                      <th className="py-3 px-4">No-Show Risk</th>
                      <th className="py-3 px-4">Tier</th>
                      <th className="py-3 px-4 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800">
                    {isLoading ? (
                      <tr>
                        <td colSpan={8} className="py-8 text-center text-slate-500">
                          Loading cohort telemetry...
                        </td>
                      </tr>
                    ) : filteredCohort.length === 0 ? (
                      <tr>
                        <td colSpan={8} className="py-8 text-center text-slate-500">
                          No patients match the selected filter.
                        </td>
                      </tr>
                    ) : (
                      filteredCohort.map((p) => {
                        const isSelected = selectedPatientId === p.encounter_id;
                        return (
                          <tr
                            key={p.encounter_id}
                            onClick={() => handleSelectPatient(p.encounter_id)}
                            className={`cursor-pointer transition-colors ${
                              isSelected ? 'bg-indigo-950/40 border-l-2 border-indigo-500' : 'hover:bg-slate-800/40'
                            }`}
                          >
                            <td className="py-3 px-4 font-mono font-medium text-white">{p.patient_mrn}</td>
                            <td className="py-3 px-4">{p.patient_age}</td>
                            <td className="py-3 px-4 text-slate-400">{p.department}</td>
                            <td className="py-3 px-4">{p.actual_los_hours}h</td>
                            <td className="py-3 px-4">
                              <span
                                className={`font-semibold ${
                                  p.predicted_readmission_risk >= 0.35
                                    ? 'text-rose-400'
                                    : p.predicted_readmission_risk >= 0.2
                                    ? 'text-amber-400'
                                    : 'text-emerald-400'
                                }`}
                              >
                                {(p.predicted_readmission_risk * 100).toFixed(1)}%
                              </span>
                            </td>
                            <td className="py-3 px-4 text-slate-400">
                              {p.predicted_noshow_risk ? `${(p.predicted_noshow_risk * 100).toFixed(1)}%` : '--'}
                            </td>
                            <td className="py-3 px-4">
                              <span
                                className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                                  p.risk_tier === 'HIGH'
                                    ? 'bg-rose-950/80 text-rose-300 border border-rose-800'
                                    : p.risk_tier === 'MODERATE'
                                    ? 'bg-amber-950/80 text-amber-300 border border-amber-800'
                                    : 'bg-emerald-950/80 text-emerald-300 border border-emerald-800'
                                }`}
                              >
                                {p.risk_tier}
                              </span>
                            </td>
                            <td className="py-3 px-4 text-right">
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleSelectPatient(p.encounter_id);
                                }}
                                className="px-2 py-1 text-[11px] bg-slate-800 hover:bg-indigo-600 text-slate-300 hover:text-white rounded transition-colors"
                              >
                                Explain SHAP
                              </button>
                            </td>
                          </tr>
                        );
                      })
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* Right Panel: Selected Patient SHAP Waterfall */}
          <div className="space-y-4">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
                <div>
                  <h3 className="font-semibold text-white text-sm">TreeSHAP Explainability Waterfall</h3>
                  <p className="text-[11px] text-slate-400">Local feature attributions relative to base rate</p>
                </div>
                {activeExplanation && (
                  <span
                    className={`px-2.5 py-1 rounded text-xs font-bold uppercase ${
                      activeExplanation.risk_tier === 'HIGH'
                        ? 'bg-rose-950 text-rose-300 border border-rose-800'
                        : activeExplanation.risk_tier === 'MODERATE'
                        ? 'bg-amber-950 text-amber-300 border border-amber-800'
                        : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                    }`}
                  >
                    {activeExplanation.risk_tier} RISK
                  </span>
                )}
              </div>

              {isExplaining ? (
                <div className="py-16 text-center text-slate-500 text-xs">
                  Calculating local TreeSHAP attribution matrix...
                </div>
              ) : activeExplanation ? (
                <div className="space-y-4">
                  {/* Summary Metric Header */}
                  <div className="grid grid-cols-2 gap-3 bg-slate-800/40 p-3 rounded-lg border border-slate-700/50">
                    <div>
                      <p className="text-[11px] text-slate-400">30-Day Readmit Score</p>
                      <p className="text-xl font-bold text-rose-400">
                        {(activeExplanation.predicted_readmission_risk * 100).toFixed(1)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-[11px] text-slate-400">No-Show Risk</p>
                      <p className="text-xl font-bold text-amber-400">
                        {activeExplanation.predicted_noshow_risk
                          ? `${(activeExplanation.predicted_noshow_risk * 100).toFixed(1)}%`
                          : 'N/A'}
                      </p>
                    </div>
                  </div>

                  {/* Outreach Recommendation */}
                  <div className="bg-indigo-950/30 border border-indigo-800/40 p-3 rounded-lg">
                    <p className="text-[10px] font-semibold text-indigo-400 uppercase tracking-wider">
                      Recommended Care Transition Outreach
                    </p>
                    <p className="text-xs text-indigo-200 mt-1 font-medium">
                      {activeExplanation.recommended_outreach}
                    </p>
                  </div>

                  {/* Waterfall Attributions */}
                  <div className="space-y-3 pt-2">
                    <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                      Feature Attributions (φ)
                    </p>

                    <div className="space-y-2">
                      {activeExplanation.feature_attributions.map((attr) => {
                        const isRisk = attr.effect === 'risk_increasing';
                        const isProtective = attr.effect === 'protective';
                        const barWidth = Math.min(Math.abs(attr.shap_value) * 60, 100);

                        return (
                          <div key={attr.feature_name} className="bg-slate-800/50 p-2.5 rounded-lg border border-slate-700/40">
                            <div className="flex items-center justify-between text-xs mb-1">
                              <span className="font-medium text-slate-200">{attr.display_name}</span>
                              <div className="flex items-center gap-2">
                                <span className="text-[11px] text-slate-400">({attr.feature_value})</span>
                                <span
                                  className={`font-mono text-xs font-bold ${
                                    isRisk ? 'text-rose-400' : isProtective ? 'text-emerald-400' : 'text-slate-400'
                                  }`}
                                >
                                  {attr.shap_value > 0 ? `+${attr.shap_value.toFixed(3)}` : attr.shap_value.toFixed(3)}
                                </span>
                              </div>
                            </div>

                            {/* Attribution Visual Bar */}
                            <div className="h-1.5 w-full bg-slate-700/60 rounded-full overflow-hidden flex">
                              {isRisk ? (
                                <div
                                  className="h-full bg-rose-500 rounded-full transition-all"
                                  style={{ width: `${barWidth}%` }}
                                ></div>
                              ) : isProtective ? (
                                <div
                                  className="h-full bg-emerald-500 rounded-full transition-all"
                                  style={{ width: `${barWidth}%` }}
                                ></div>
                              ) : (
                                <div className="h-full bg-slate-500 rounded-full w-1"></div>
                              )}
                            </div>

                            <p className="text-[10px] text-slate-400 mt-1.5 leading-snug">
                              {attr.clinical_interpretation}
                            </p>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="py-16 text-center text-slate-500 text-xs">
                  Select a patient encounter from the table to view personalized TreeSHAP risk attributions.
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Interactive Ad-Hoc Simulator */}
      {activeTab === 'simulator' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Controls */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-5">
            <div>
              <h3 className="font-semibold text-white text-base">Patient Risk Simulation Parameters</h3>
              <p className="text-xs text-slate-400">
                Adjust clinical characteristics to evaluate model sensitivity and observe live SHAP impact.
              </p>
            </div>

            {/* Slider: Patient Age */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="text-slate-300 font-medium">Patient Age</span>
                <span className="text-indigo-400 font-bold font-mono">{simAge} years</span>
              </div>
              <input
                type="range"
                min="18"
                max="95"
                value={simAge}
                onChange={(e) => setSimAge(Number(e.target.value))}
                className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-500"
              />
            </div>

            {/* Slider: Triage ESI */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="text-slate-300 font-medium">Emergency Triage Acuity (ESI)</span>
                <span className="text-amber-400 font-bold font-mono">ESI {simEsi} ({simEsi <= 2 ? 'Emergent' : 'Urgent/Non-urgent'})</span>
              </div>
              <input
                type="range"
                min="1"
                max="5"
                value={simEsi}
                onChange={(e) => setSimEsi(Number(e.target.value))}
                className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-amber-500"
              />
            </div>

            {/* Slider: Length of Stay */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="text-slate-300 font-medium">Length of Stay (Inpatient Hours)</span>
                <span className="text-indigo-400 font-bold font-mono">{simLos} hours ({(simLos / 24).toFixed(1)} days)</span>
              </div>
              <input
                type="range"
                min="6"
                max="240"
                step="6"
                value={simLos}
                onChange={(e) => setSimLos(Number(e.target.value))}
                className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-500"
              />
            </div>

            {/* Slider: Prior Admissions */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="text-slate-300 font-medium">Prior Hospital Admissions (Past 12 Months)</span>
                <span className="text-rose-400 font-bold font-mono">{simPriors} prior encounters</span>
              </div>
              <input
                type="range"
                min="0"
                max="6"
                value={simPriors}
                onChange={(e) => setSimPriors(Number(e.target.value))}
                className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-rose-500"
              />
            </div>

            {/* Slider: Comorbidities */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="text-slate-300 font-medium">Documented Chronic Comorbidities</span>
                <span className="text-amber-400 font-bold font-mono">{simComorb} conditions</span>
              </div>
              <input
                type="range"
                min="0"
                max="5"
                value={simComorb}
                onChange={(e) => setSimComorb(Number(e.target.value))}
                className="w-full h-1.5 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-amber-500"
              />
            </div>

            {/* Toggles & Text */}
            <div className="grid grid-cols-2 gap-4 pt-2">
              <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-300">
                <input
                  type="checkbox"
                  checked={simIsEmerg}
                  onChange={(e) => setSimIsEmerg(e.target.checked)}
                  className="rounded bg-slate-800 border-slate-700 text-indigo-600 focus:ring-0"
                />
                <span>Emergency Admission</span>
              </label>

              <label className="flex items-center gap-2 cursor-pointer text-xs text-slate-300">
                <input
                  type="checkbox"
                  checked={simDischargeHome}
                  onChange={(e) => setSimDischargeHome(e.target.checked)}
                  className="rounded bg-slate-800 border-slate-700 text-indigo-600 focus:ring-0"
                />
                <span>Discharge to Home</span>
              </label>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs text-slate-300 font-medium">Chief Complaint / Key Diagnosis</label>
              <input
                type="text"
                value={simComplaint}
                onChange={(e) => setSimComplaint(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-lg px-3 py-2 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <button
              onClick={handleRunSimulation}
              disabled={isSimulating}
              className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs rounded-lg transition-colors shadow-md flex items-center justify-center gap-2"
            >
              {isSimulating ? 'Evaluating TreeSHAP...' : '⚡ Recompute TreeSHAP Waterfall'}
            </button>
          </div>

          {/* Simulation Output */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-lg space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="font-semibold text-white text-base">Model Response & Waterfall</h3>
                <p className="text-xs text-slate-400">Explainable risk estimation for simulated profile</p>
              </div>
              {simResult && (
                <span
                  className={`px-2.5 py-1 rounded text-xs font-bold uppercase ${
                    simResult.risk_tier === 'HIGH'
                      ? 'bg-rose-950 text-rose-300 border border-rose-800'
                      : simResult.risk_tier === 'MODERATE'
                      ? 'bg-amber-950 text-amber-300 border border-amber-800'
                      : 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                  }`}
                >
                  {simResult.risk_tier} RISK
                </span>
              )}
            </div>

            {simResult && (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-3 bg-slate-800/40 p-3 rounded-lg border border-slate-700/50">
                  <div>
                    <p className="text-[11px] text-slate-400">30-Day Readmission Risk</p>
                    <p className="text-2xl font-bold text-rose-400">
                      {(simResult.predicted_readmission_risk * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-[11px] text-slate-400">Appointment No-Show Risk</p>
                    <p className="text-2xl font-bold text-amber-400">
                      {simResult.predicted_noshow_risk
                        ? `${(simResult.predicted_noshow_risk * 100).toFixed(1)}%`
                        : 'N/A'}
                    </p>
                  </div>
                </div>

                <div className="bg-indigo-950/30 border border-indigo-800/40 p-3 rounded-lg">
                  <p className="text-[10px] font-semibold text-indigo-400 uppercase tracking-wider">
                    Recommended Care Transition Outreach
                  </p>
                  <p className="text-xs text-indigo-200 mt-1 font-medium">{simResult.recommended_outreach}</p>
                </div>

                <div className="space-y-2 pt-2">
                  <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                    Feature Impact Waterfall (TreeSHAP)
                  </p>
                  {simResult.feature_attributions.map((attr) => {
                    const isRisk = attr.effect === 'risk_increasing';
                    const isProtective = attr.effect === 'protective';
                    const barWidth = Math.min(Math.abs(attr.shap_value) * 60, 100);

                    return (
                      <div key={attr.feature_name} className="bg-slate-800/50 p-2.5 rounded-lg border border-slate-700/40">
                        <div className="flex items-center justify-between text-xs mb-1">
                          <span className="font-medium text-slate-200">{attr.display_name}</span>
                          <div className="flex items-center gap-2">
                            <span className="text-[11px] text-slate-400">({attr.feature_value})</span>
                            <span
                              className={`font-mono text-xs font-bold ${
                                isRisk ? 'text-rose-400' : isProtective ? 'text-emerald-400' : 'text-slate-400'
                              }`}
                            >
                              {attr.shap_value > 0 ? `+${attr.shap_value.toFixed(3)}` : attr.shap_value.toFixed(3)}
                            </span>
                          </div>
                        </div>

                        <div className="h-1.5 w-full bg-slate-700/60 rounded-full overflow-hidden flex">
                          {isRisk ? (
                            <div className="h-full bg-rose-500 rounded-full" style={{ width: `${barWidth}%` }}></div>
                          ) : isProtective ? (
                            <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${barWidth}%` }}></div>
                          ) : (
                            <div className="h-full bg-slate-500 rounded-full w-1"></div>
                          )}
                        </div>

                        <p className="text-[10px] text-slate-400 mt-1.5 leading-snug">
                          {attr.clinical_interpretation}
                        </p>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
