import React, { useState, useEffect } from 'react';
import {
  Building2,
  Navigation,
  Truck,
  AlertOctagon,
  CheckCircle2,
  RefreshCw,
  Clock,
  ArrowRight,
  MapPin,
  Activity,
  Send
} from 'lucide-react';
import {
  fetchRegionalNetworkStatus,
  fetchRegionalTransferRecommendations,
  dispatchRegionalTransfer,
  toggleRegionalDiversion
} from '../services/api';
import {
  RegionalNetworkStatusResponse,
  RegionalTransferOptimizationResponse,
  HospitalFacilityTelemetry
} from '../types';

export const RegionalNetworkPage: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = useState<'FACILITIES' | 'TRANSFERS' | 'DIVERSIONS' | 'TRANSIT'>('FACILITIES');
  const [networkData, setNetworkData] = useState<RegionalNetworkStatusResponse | null>(null);
  const [transferData, setTransferData] = useState<RegionalTransferOptimizationResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [dispatchStatus, setDispatchStatus] = useState<Record<string, string>>({});
  const [diversionStatusMessage, setDiversionStatusMessage] = useState<string>('');
  const [notesInput, setNotesInput] = useState<Record<string, string>>({});

  useEffect(() => {
    loadRegionalData();
  }, []);

  const loadRegionalData = async () => {
    setIsLoading(true);
    try {
      const [network, transfers] = await Promise.all([
        fetchRegionalNetworkStatus(),
        fetchRegionalTransferRecommendations()
      ]);
      setNetworkData(network);
      setTransferData(transfers);
    } catch (err) {
      console.error('Failed to load regional telemetry:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDispatch = async (transferId: string) => {
    try {
      setDispatchStatus((prev) => ({ ...prev, [transferId]: 'DISPATCHING...' }));
      const notes = notesInput[transferId] || 'Authorized by Regional Command Operations';
      const res = await dispatchRegionalTransfer(transferId, notes, 'CRITICAL_CARE_AMBULANCE');
      setDispatchStatus((prev) => ({ ...prev, [transferId]: `DISPATCHED: ${res.destination_hospital}` }));
      await loadRegionalData();
    } catch {
      setDispatchStatus((prev) => ({ ...prev, [transferId]: 'ERROR DISPATCHING' }));
    }
  };

  const handleToggleDiversion = async (hospitalId: string, currentStatus: string) => {
    try {
      const newStatus = currentStatus === 'DIVERT_OVERFLOW' ? 'NORMAL' : 'DIVERT_OVERFLOW';
      const reason = newStatus === 'DIVERT_OVERFLOW'
        ? 'Emergency department capacity saturated; critical trauma diversion activated'
        : 'Emergency intake normalized; normal admission protocol restored';

      setDiversionStatusMessage(`Updating ${hospitalId}...`);
      const res = await toggleRegionalDiversion(hospitalId, newStatus, reason);
      setDiversionStatusMessage(`Updated: ${res.message}`);
      setTimeout(() => setDiversionStatusMessage(''), 4000);
      await loadRegionalData();
    } catch {
      setDiversionStatusMessage('Failed to update diversion status.');
    }
  };

  const stressIndex = networkData?.network_stress_index ?? 50.0;

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 p-4 opacity-10 pointer-events-none">
          <Building2 className="w-64 h-64 text-teal-400" />
        </div>

        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 relative z-10">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-teal-500/20 text-teal-300 border border-teal-500/30">
                Phase 8 Regional Architecture
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-800 text-slate-300 border border-slate-700">
                {networkData?.total_facilities ?? 4} Facilities Connected
              </span>
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">
              Regional Multi-Hospital Network & Transfer Command
            </h1>
            <p className="text-slate-400 text-sm mt-0.5">
              Cross-facility capacity balancing, PuLP inter-hospital transfer optimization, and emergency ambulance diversion management
            </p>
          </div>

          <button
            onClick={loadRegionalData}
            disabled={isLoading}
            className="flex items-center gap-2 px-4 py-2 bg-teal-600 hover:bg-teal-500 text-white text-sm font-medium rounded-lg shadow-lg shadow-teal-600/30 transition disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh Telemetry
          </button>
        </div>

        {/* Regional KPI Strip */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mt-6 pt-5 border-t border-slate-800/80">
          <div className="bg-slate-800/60 p-3 rounded-lg border border-slate-700/50">
            <div className="text-xs font-medium text-slate-400 flex items-center justify-between">
              Regional Stress Index
              <Activity className="w-3.5 h-3.5 text-teal-400" />
            </div>
            <div className="flex items-baseline gap-2 mt-1">
              <span
                className={`text-2xl font-bold ${
                  stressIndex < 60
                    ? 'text-emerald-400'
                    : stressIndex < 80
                    ? 'text-amber-400'
                    : 'text-rose-400'
                }`}
              >
                {stressIndex}
              </span>
              <span className="text-xs text-slate-500">/ 100</span>
            </div>
            <div className="w-full bg-slate-700 h-1.5 rounded-full mt-2 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  stressIndex < 60
                    ? 'bg-emerald-500'
                    : stressIndex < 80
                    ? 'bg-amber-500'
                    : 'bg-rose-500'
                }`}
                style={{ width: `${stressIndex}%` }}
              />
            </div>
          </div>

          <div className="bg-slate-800/60 p-3 rounded-lg border border-slate-700/50">
            <div className="text-xs font-medium text-slate-400 flex items-center justify-between">
              Network Staffed Beds
              <Building2 className="w-3.5 h-3.5 text-teal-400" />
            </div>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-2xl font-bold text-white">
                {networkData?.network_staffed_beds ?? 0}
              </span>
              <span className="text-xs text-slate-400">
                ({networkData?.network_physical_beds ?? 0} Phys)
              </span>
            </div>
            <div className="text-xs text-slate-400 mt-2 truncate">
              Across 4 health facilities
            </div>
          </div>

          <div className="bg-slate-800/60 p-3 rounded-lg border border-slate-700/50">
            <div className="text-xs font-medium text-slate-400 flex items-center justify-between">
              Network Occupancy
              <Activity className="w-3.5 h-3.5 text-indigo-400" />
            </div>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-2xl font-bold text-indigo-400">
                {networkData?.network_occupancy_pct ?? 0}%
              </span>
              <span className="text-xs text-slate-400">
                {networkData?.network_occupied_beds ?? 0} occupied
              </span>
            </div>
            <div className="text-xs text-slate-400 mt-2">
              Staffed beds utilized
            </div>
          </div>

          <div className="bg-slate-800/60 p-3 rounded-lg border border-slate-700/50">
            <div className="text-xs font-medium text-slate-400 flex items-center justify-between">
              Active Diversions
              <AlertOctagon className="w-3.5 h-3.5 text-rose-400" />
            </div>
            <div className="flex items-baseline gap-2 mt-1">
              <span
                className={`text-2xl font-bold ${
                  (networkData?.active_diversions_count ?? 0) > 0
                    ? 'text-rose-400'
                    : 'text-emerald-400'
                }`}
              >
                {networkData?.active_diversions_count ?? 0}
              </span>
              <span className="text-xs text-slate-400">facilities</span>
            </div>
            <div className="text-xs text-slate-400 mt-2">
              Ambulance overflow diversion
            </div>
          </div>

          <div className="bg-slate-800/60 p-3 rounded-lg border border-slate-700/50">
            <div className="text-xs font-medium text-slate-400 flex items-center justify-between">
              Recommended Transfers
              <Truck className="w-3.5 h-3.5 text-teal-400" />
            </div>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-2xl font-bold text-teal-400">
                {transferData?.total_transfers_recommended ?? 0}
              </span>
              <span className="text-xs text-emerald-400">PuLP Optimal</span>
            </div>
            <div className="text-xs text-slate-400 mt-2">
              Load rebalancing queue
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Sub-Tabs */}
      <div className="flex border-b border-slate-800 gap-2">
        <button
          onClick={() => setActiveSubTab('FACILITIES')}
          className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition ${
            activeSubTab === 'FACILITIES'
              ? 'border-teal-500 text-teal-400 bg-teal-500/10'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Building2 className="w-4 h-4" />
          Network Facilities
          <span className="px-1.5 py-0.5 text-xs rounded-full bg-slate-800 text-slate-300">
            {networkData?.facilities.length ?? 4}
          </span>
        </button>

        <button
          onClick={() => setActiveSubTab('TRANSFERS')}
          className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition ${
            activeSubTab === 'TRANSFERS'
              ? 'border-teal-500 text-teal-400 bg-teal-500/10'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Truck className="w-4 h-4" />
          Transfer Optimization Deck
          {transferData && transferData.total_transfers_recommended > 0 && (
            <span className="px-1.5 py-0.5 text-xs rounded-full bg-teal-500 text-slate-950 font-bold">
              {transferData.total_transfers_recommended}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveSubTab('DIVERSIONS')}
          className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition ${
            activeSubTab === 'DIVERSIONS'
              ? 'border-teal-500 text-teal-400 bg-teal-500/10'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <AlertOctagon className="w-4 h-4" />
          Emergency Diversion Control
          {networkData && networkData.active_diversions_count > 0 && (
            <span className="px-1.5 py-0.5 text-xs rounded-full bg-rose-500 text-white font-bold">
              {networkData.active_diversions_count}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveSubTab('TRANSIT')}
          className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition ${
            activeSubTab === 'TRANSIT'
              ? 'border-teal-500 text-teal-400 bg-teal-500/10'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Navigation className="w-4 h-4" />
          Regional Transit Matrix
        </button>
      </div>

      {/* SUB-TAB 1: FACILITIES */}
      {activeSubTab === 'FACILITIES' && networkData && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {networkData.facilities.map((fac: HospitalFacilityTelemetry) => (
              <div
                key={fac.hospital_id}
                className={`p-5 rounded-xl border bg-slate-900 transition-all ${
                  fac.diversion_status === 'DIVERT_OVERFLOW'
                    ? 'border-rose-500/50 shadow-lg shadow-rose-950/20'
                    : fac.diversion_status === 'ADVISORY'
                    ? 'border-amber-500/50 shadow-lg shadow-amber-950/20'
                    : 'border-slate-800'
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-2.5">
                    <div className="p-2.5 rounded-lg bg-teal-500/10 text-teal-400 border border-teal-500/20">
                      <Building2 className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-2xs font-bold uppercase tracking-wider text-slate-400">
                          {fac.hospital_id} • {fac.facility_type.replace(/_/g, ' ')}
                        </span>
                      </div>
                      <h3 className="text-base font-bold text-white mt-0.5">
                        {fac.hospital_name}
                      </h3>
                      <div className="flex items-center gap-1 text-xs text-slate-400 mt-0.5">
                        <MapPin className="w-3 h-3 text-slate-500" />
                        {fac.location}
                      </div>
                    </div>
                  </div>

                  <span
                    className={`px-2 py-0.5 rounded text-xs font-bold ${
                      fac.diversion_status === 'DIVERT_OVERFLOW'
                        ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                        : fac.diversion_status === 'ADVISORY'
                        ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                        : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    }`}
                  >
                    {fac.diversion_status}
                  </span>
                </div>

                {/* Capacity Metrics */}
                <div className="grid grid-cols-4 gap-2 mt-4 pt-3 border-t border-slate-800/80 text-xs">
                  <div className="bg-slate-800/40 p-2 rounded">
                    <div className="text-slate-400 text-2xs">Staffed Capacity</div>
                    <div className="font-semibold text-white mt-0.5">
                      {fac.occupied_beds} / {fac.staffed_usable_beds}
                    </div>
                  </div>

                  <div className="bg-slate-800/40 p-2 rounded">
                    <div className="text-slate-400 text-2xs">Staffed Occupancy</div>
                    <div
                      className={`font-semibold mt-0.5 ${
                        fac.staffed_occupancy_pct >= 90
                          ? 'text-rose-400'
                          : fac.staffed_occupancy_pct >= 80
                          ? 'text-amber-400'
                          : 'text-emerald-400'
                      }`}
                    >
                      {fac.staffed_occupancy_pct}%
                    </div>
                  </div>

                  <div className="bg-slate-800/40 p-2 rounded">
                    <div className="text-slate-400 text-2xs">ICU Occupancy</div>
                    <div className="font-semibold text-white mt-0.5">
                      {fac.icu_occupancy_pct}%
                    </div>
                  </div>

                  <div className="bg-slate-800/40 p-2 rounded">
                    <div className="text-slate-400 text-2xs">ED Wait Time</div>
                    <div
                      className={`font-semibold mt-0.5 ${
                        fac.ed_wait_time_minutes > 90 ? 'text-rose-400' : 'text-slate-300'
                      }`}
                    >
                      {fac.ed_wait_time_minutes}m
                    </div>
                  </div>
                </div>

                {/* Occupancy Progress Bar */}
                <div className="w-full bg-slate-800 h-1.5 rounded-full mt-3 overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      fac.staffed_occupancy_pct >= 90
                        ? 'bg-rose-500'
                        : fac.staffed_occupancy_pct >= 80
                        ? 'bg-amber-500'
                        : 'bg-teal-500'
                    }`}
                    style={{ width: `${Math.min(fac.staffed_occupancy_pct, 100)}%` }}
                  />
                </div>

                {/* Specialties Available */}
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {fac.specialties_available.map((spec) => (
                    <span
                      key={spec}
                      className="px-2 py-0.5 rounded text-2xs bg-slate-800/80 text-slate-300 border border-slate-700/50"
                    >
                      {spec}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SUB-TAB 2: TRANSFERS (PuLP Optimization Deck) */}
      {activeSubTab === 'TRANSFERS' && (
        <div className="space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Truck className="w-5 h-5 text-teal-400" />
              PuLP Mixed-Integer Linear Programming Regional Transfer Engine
            </h2>
            <p className="text-slate-400 text-xs mt-1">
              Optimizes cross-facility patient transfers to minimize network occupancy variance while strictly respecting destination clinical acuity capabilities and ambulance transit travel times.
            </p>
          </div>

          {transferData && transferData.transfers.length > 0 ? (
            <div className="space-y-4">
              {transferData.transfers.map((rec) => (
                <div
                  key={rec.transfer_id}
                  className="p-5 rounded-xl border border-slate-800 bg-slate-900 transition"
                >
                  <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-3">
                    <div className="flex items-center gap-2">
                      <span
                        className={`px-2 py-0.5 rounded text-xs font-bold ${
                          rec.urgency === 'IMMEDIATE'
                            ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                            : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                        }`}
                      >
                        {rec.urgency}
                      </span>
                      <span className="text-xs text-slate-400">
                        Patient: <strong className="text-white">{rec.patient_anon_id}</strong> • Acuity: <strong className="text-indigo-300">{rec.triage_acuity}</strong> • Specialty: <strong className="text-teal-300">{rec.specialty_required}</strong>
                      </span>
                    </div>

                    <span
                      className={`text-xs px-2.5 py-1 rounded-full font-medium ${
                        rec.status === 'DISPATCHED'
                          ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                          : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      Status: {rec.status}
                    </span>
                  </div>

                  {/* Transfer Route Vector */}
                  <div className="mt-3 p-3 bg-slate-950/60 rounded-lg border border-slate-800 flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <Building2 className="w-4 h-4 text-rose-400" />
                      <span className="font-semibold text-white">{rec.source_hospital_name}</span>
                    </div>

                    <div className="flex items-center gap-2 text-teal-400 font-mono text-xs">
                      <span>{rec.transit_distance_km} km</span>
                      <ArrowRight className="w-4 h-4 text-teal-400" />
                      <span>{rec.transit_time_minutes} mins</span>
                    </div>

                    <div className="flex items-center gap-2">
                      <Building2 className="w-4 h-4 text-emerald-400" />
                      <span className="font-semibold text-white">{rec.destination_hospital_name}</span>
                    </div>
                  </div>

                  {/* Clinical Justification */}
                  <div className="mt-3 text-xs bg-slate-950/40 p-3 rounded border border-slate-800/80">
                    <span className="font-semibold text-slate-400">Clinical Rationalization: </span>
                    <span className="text-slate-300">{rec.clinical_justification}</span>
                  </div>

                  {/* Dispatch Controls */}
                  <div className="mt-4 pt-3 border-t border-slate-800 flex flex-col md:flex-row items-center justify-between gap-3">
                    <div className="w-full md:w-2/3">
                      <input
                        type="text"
                        placeholder="Transfer dispatch authorization notes (persisted in audit log)..."
                        value={notesInput[rec.transfer_id] || ''}
                        onChange={(e) =>
                          setNotesInput({
                            ...notesInput,
                            [rec.transfer_id]: e.target.value
                          })
                        }
                        className="w-full px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-teal-500"
                      />
                    </div>

                    <div className="flex items-center gap-3 w-full md:w-auto justify-end">
                      {dispatchStatus[rec.transfer_id] && (
                        <span className="text-xs text-teal-400 font-medium">
                          {dispatchStatus[rec.transfer_id]}
                        </span>
                      )}
                      <button
                        onClick={() => handleDispatch(rec.transfer_id)}
                        disabled={rec.status === 'DISPATCHED'}
                        className="flex items-center gap-1.5 px-4 py-1.5 bg-teal-600 hover:bg-teal-500 disabled:bg-slate-800 disabled:text-slate-600 text-white text-xs font-semibold rounded-lg shadow-md transition"
                      >
                        <Send className="w-3.5 h-3.5" />
                        Dispatch Ambulance Unit
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center">
              <CheckCircle2 className="w-12 h-12 text-teal-400 mx-auto mb-3" />
              <h3 className="text-lg font-semibold text-white">Regional Census Balanced</h3>
              <p className="text-slate-400 text-sm max-w-md mx-auto mt-1">
                The PuLP transfer solver verified that all network hospitals are operating below saturated thresholds; no inter-facility transfers required.
              </p>
            </div>
          )}
        </div>
      )}

      {/* SUB-TAB 3: DIVERSIONS */}
      {activeSubTab === 'DIVERSIONS' && networkData && (
        <div className="space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <AlertOctagon className="w-5 h-5 text-rose-400" />
              Emergency Ambulance Diversion Protocol Matrix
            </h2>
            <p className="text-slate-400 text-xs mt-1">
              Direct emergency dispatchers to re-route incoming ambulance intake when acute overcrowding occurs. Authorizing status changes triggers compliance audit entries and broadcasts live WebSocket alerts.
            </p>

            {diversionStatusMessage && (
              <div className="mt-3 p-3 bg-teal-950/60 border border-teal-800/80 rounded-lg text-xs text-teal-200">
                {diversionStatusMessage}
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {networkData.facilities.map((fac) => (
              <div
                key={fac.hospital_id}
                className="bg-slate-900 border border-slate-800 rounded-xl p-5"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-bold text-white">{fac.hospital_name}</h3>
                    <p className="text-xs text-slate-400 mt-0.5">{fac.facility_type.replace(/_/g, ' ')}</p>
                  </div>
                  <span
                    className={`px-2 py-0.5 rounded text-xs font-bold ${
                      fac.diversion_status === 'DIVERT_OVERFLOW'
                        ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                        : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    }`}
                  >
                    {fac.diversion_status}
                  </span>
                </div>

                <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
                  <div className="bg-slate-800/40 p-2 rounded">
                    <span className="text-slate-400 text-2xs block">Staffed Occupancy</span>
                    <span className="font-semibold text-white">{fac.staffed_occupancy_pct}%</span>
                  </div>
                  <div className="bg-slate-800/40 p-2 rounded">
                    <span className="text-slate-400 text-2xs block">ED Triage Wait</span>
                    <span className="font-semibold text-white">{fac.ed_wait_time_minutes} mins</span>
                  </div>
                </div>

                <button
                  onClick={() => handleToggleDiversion(fac.hospital_id, fac.diversion_status)}
                  className={`mt-4 w-full py-2 rounded-lg text-xs font-semibold shadow-md transition flex items-center justify-center gap-1.5 ${
                    fac.diversion_status === 'DIVERT_OVERFLOW'
                      ? 'bg-emerald-600 hover:bg-emerald-500 text-white'
                      : 'bg-rose-600 hover:bg-rose-500 text-white'
                  }`}
                >
                  <AlertOctagon className="w-3.5 h-3.5" />
                  {fac.diversion_status === 'DIVERT_OVERFLOW'
                    ? 'Lift Diversion (Restore Intake)'
                    : 'Activate Ambulance Diversion (Divert Overflow)'}
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SUB-TAB 4: TRANSIT */}
      {activeSubTab === 'TRANSIT' && networkData && (
        <div className="space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Navigation className="w-5 h-5 text-teal-400" />
              Regional Inter-Facility Transit Matrix
            </h2>
            <p className="text-slate-400 text-xs mt-1">
              Highway and arterial corridor transit times (minutes) and distance (km) utilized by the PuLP transfer optimization solver.
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950/80 text-2xs font-semibold text-slate-400 border-b border-slate-800">
                <tr>
                  <th className="p-3">ORIGIN HOSPITAL</th>
                  <th className="p-3">DESTINATION HOSPITAL</th>
                  <th className="p-3">TRANSIT DISTANCE</th>
                  <th className="p-3">AMBULANCE TRAVEL TIME</th>
                  <th className="p-3">CORRIDOR STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono text-xs">
                {networkData.transit_matrix.map((t, idx) => (
                  <tr key={idx} className="hover:bg-slate-800/40 transition">
                    <td className="p-3 font-semibold text-white">{t.origin_hospital_id}</td>
                    <td className="p-3 font-semibold text-teal-300">{t.destination_hospital_id}</td>
                    <td className="p-3 text-slate-300">{t.distance_km} km</td>
                    <td className="p-3 text-indigo-300 font-semibold flex items-center gap-1.5">
                      <Clock className="w-3 h-3 text-indigo-400" />
                      {t.transit_time_minutes} minutes
                    </td>
                    <td className="p-3 text-emerald-400 font-sans text-2xs">CLEAR • ACTIVE</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

