import React, { useState } from 'react';
import { BedDouble, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { Bed, WardCapacitySummary, BedState } from '../../types';

interface BedMatrixProps {
  wards: WardCapacitySummary[];
  beds: Bed[];
  isLoading: boolean;
  onStateChange: (bedId: string, newState: BedState, reason?: string) => Promise<void>;
}

const STATE_CONFIG: Record<BedState, { label: string; bg: string; border: string; text: string }> = {
  Ready: { label: 'Ready', bg: 'bg-emerald-500/10', border: 'border-emerald-500/30', text: 'text-emerald-400' },
  Reserved: { label: 'Reserved', bg: 'bg-sky-500/10', border: 'border-sky-500/30', text: 'text-sky-400' },
  Occupied: { label: 'Occupied', bg: 'bg-rose-500/10', border: 'border-rose-500/30', text: 'text-rose-400' },
  Cleaning: { label: 'Cleaning', bg: 'bg-amber-500/10', border: 'border-amber-500/30', text: 'text-amber-400' },
  Maintenance: { label: 'Maintenance', bg: 'bg-orange-500/10', border: 'border-orange-500/30', text: 'text-orange-400' },
  Blocked: { label: 'Blocked', bg: 'bg-slate-700/20', border: 'border-slate-600/30', text: 'text-slate-400' },
};

const VALID_TRANSITIONS: Record<BedState, BedState[]> = {
  Ready: ['Reserved', 'Occupied', 'Blocked'],
  Reserved: ['Occupied', 'Ready', 'Blocked'],
  Occupied: ['Cleaning'],
  Cleaning: ['Ready', 'Blocked', 'Maintenance'],
  Maintenance: ['Cleaning', 'Blocked'],
  Blocked: ['Maintenance', 'Cleaning', 'Ready'],
};

export const BedMatrix: React.FC<BedMatrixProps> = ({
  wards,
  beds,
  isLoading,
  onStateChange,
}) => {
  const [selectedWard, setSelectedWard] = useState<string>('ALL');
  const [activeBedModal, setActiveBedModal] = useState<Bed | null>(null);
  const [transitionError, setTransitionError] = useState<string | null>(null);
  const [isUpdating, setIsUpdating] = useState(false);

  if (isLoading) {
    return (
      <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl animate-pulse h-96">
        <div className="h-6 w-48 bg-slate-800 rounded mb-4"></div>
        <div className="grid grid-cols-4 gap-4 h-64 bg-slate-800/30 rounded"></div>
      </div>
    );
  }

  const filteredWards = selectedWard === 'ALL' ? wards : wards.filter((w) => w.ward_id === selectedWard);

  const handleTransition = async (newState: BedState) => {
    if (!activeBedModal) return;
    setIsUpdating(true);
    setTransitionError(null);
    try {
      await onStateChange(activeBedModal.id, newState, `Operator updated to ${newState}`);
      setActiveBedModal(null);
    } catch (err: any) {
      const msg = err.response?.data?.detail || err.message || 'Illegal transition attempted.';
      setTransitionError(msg);
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-6">
      {/* Header and Ward Filter */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <BedDouble className="w-5 h-5 text-indigo-400" />
            <h2 className="text-base font-bold text-white">Module 2: Operational Bed Matrix & Lifecycle States</h2>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Real-time physical vs staffed usable capacity tracking across 8 hospital units
          </p>
        </div>

        {/* Filter Pills */}
        <div className="flex flex-wrap gap-1.5 bg-slate-950 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setSelectedWard('ALL')}
            className={`px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
              selectedWard === 'ALL'
                ? 'bg-indigo-500 text-white'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
            }`}
          >
            All Wards ({wards.length})
          </button>
          {wards.map((w) => (
            <button
              key={w.ward_id}
              onClick={() => setSelectedWard(w.ward_id)}
              className={`px-2.5 py-1 text-xs font-semibold rounded-lg transition-all ${
                selectedWard === w.ward_id
                  ? 'bg-indigo-500 text-white'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              {w.ward_code}
            </button>
          ))}
        </div>
      </div>

      {/* Ward Cards with Usable Staffed Capacity */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {filteredWards.map((w) => {
          const wardBeds = beds.filter((b) => b.ward_id === w.ward_id);
          const hasDeficit = w.staffing_deficit;

          return (
            <div
              key={w.ward_id}
              className="bg-slate-950/60 border border-slate-800/80 rounded-xl p-4 space-y-3"
            >
              {/* Ward Header */}
              <div className="flex items-center justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-bold text-white text-sm">{w.ward_name}</h3>
                    <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded-full bg-slate-800 text-slate-300">
                      {w.specialty}
                    </span>
                  </div>
                  <div className="text-xs text-slate-400 mt-0.5">
                    Nurses on duty: <span className="font-semibold text-slate-200">{w.on_duty_nurses}</span> (Ceiling: {w.nurse_capacity_ceiling} pts)
                  </div>
                </div>

                {/* Staffed Usable Capacity Badge */}
                <div className="text-right">
                  <div className="text-xs font-medium text-slate-400">Staffed Usable</div>
                  <div className="text-lg font-extrabold text-emerald-400">
                    {w.staffed_usable_beds} <span className="text-xs text-slate-500">/ {w.ready_beds} ready</span>
                  </div>
                </div>
              </div>

              {/* Staffing Alert Warning */}
              {hasDeficit && (
                <div className="flex items-center gap-2 p-2 bg-amber-500/10 border border-amber-500/20 rounded-lg text-xs text-amber-300">
                  <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" />
                  <span>
                    Staffing deficit: {w.unstaffed_ready_beds} clean bed(s) unstaffed due to nurse ratio limit.
                  </span>
                </div>
              )}

              {/* Bed Tiles Grid */}
              <div className="grid grid-cols-5 sm:grid-cols-8 gap-2 pt-1">
                {wardBeds.map((bed) => {
                  const cfg = STATE_CONFIG[bed.current_state] || STATE_CONFIG.Ready;
                  return (
                    <button
                      key={bed.id}
                      onClick={() => {
                        setActiveBedModal(bed);
                        setTransitionError(null);
                      }}
                      className={`p-2 rounded-lg border text-center transition-all hover:scale-105 ${cfg.bg} ${cfg.border}`}
                      title={`${bed.bed_number}: ${bed.current_state}`}
                    >
                      <div className={`text-[11px] font-bold ${cfg.text}`}>{bed.bed_number.split('-')[1]}</div>
                      <div className="text-[8px] uppercase tracking-wider text-slate-400 truncate mt-0.5">
                        {bed.current_state}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      {/* State Machine Transition Modal */}
      {activeBedModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 max-w-md w-full rounded-2xl p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <div>
                <h3 className="text-base font-bold text-white">Bed State Machine Transition</h3>
                <p className="text-xs text-slate-400">Bed: <span className="font-semibold text-white">{activeBedModal.bed_number}</span></p>
              </div>
              <button
                onClick={() => setActiveBedModal(null)}
                className="text-slate-400 hover:text-white text-lg font-bold"
              >
                ✕
              </button>
            </div>

            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Current Lifecycle State:</span>
                <span className={`font-bold ${STATE_CONFIG[activeBedModal.current_state].text}`}>
                  {activeBedModal.current_state}
                </span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Isolation Capable:</span>
                <span className="text-slate-200">{activeBedModal.is_isolation_capable ? 'Yes' : 'No'}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Telemetry Capable:</span>
                <span className="text-slate-200">{activeBedModal.is_telemetry_capable ? 'Yes' : 'No'}</span>
              </div>
            </div>

            {/* Error banner if illegal transition */}
            {transitionError && (
              <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-xs text-rose-400 flex items-start gap-2">
                <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                <span>{transitionError}</span>
              </div>
            )}

            {/* Permitted Transition Actions */}
            <div>
              <div className="text-xs font-semibold text-slate-300 mb-2">Permitted Transitions:</div>
              <div className="grid grid-cols-2 gap-2">
                {VALID_TRANSITIONS[activeBedModal.current_state]?.map((targetState) => {
                  const cfg = STATE_CONFIG[targetState];
                  return (
                    <button
                      key={targetState}
                      disabled={isUpdating}
                      onClick={() => handleTransition(targetState)}
                      className={`p-2.5 rounded-xl border text-xs font-bold transition-all text-left flex items-center justify-between ${cfg.bg} ${cfg.border} ${cfg.text} hover:opacity-90`}
                    >
                      <span>➔ {targetState}</span>
                      <CheckCircle2 className="w-3.5 h-3.5" />
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="pt-2 text-[11px] text-slate-500 italic">
              Note: Unapproved transitions (such as Cleaning ➔ Occupied) violate protocol and are rejected by the backend state validator.
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
