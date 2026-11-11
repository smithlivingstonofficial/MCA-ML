import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Package,
  Pill,
  Wind,
  Activity,
  AlertTriangle,
  CheckCircle2,
  Users,
  TrendingDown
} from 'lucide-react';
import {
  fetchInventoryItems,
  dispenseMedication,
  fetchEquipmentTelemetry,
  fetchWorkforceDeficits,
  fetchRoster,
  updateStaffStatus
} from '../services/api';
import { InventoryItem, DispenseResponse } from '../types';

export const ResourceIntelligencePage: React.FC = () => {
  const queryClient = useQueryClient();
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [selectedShift, setSelectedShift] = useState<string>('Morning');
  
  // Dispense Modal State
  const [dispenseItem, setDispenseItem] = useState<InventoryItem | null>(null);
  const [dispenseQty, setDispenseQty] = useState<number>(5);
  const [dispenseResult, setDispenseResult] = useState<DispenseResponse | null>(null);
  const [dispenseError, setDispenseError] = useState<string | null>(null);

  // Queries
  const { data: items, isLoading: loadingItems } = useQuery({
    queryKey: ['inventory', selectedCategory],
    queryFn: () => fetchInventoryItems(selectedCategory),
    refetchInterval: 30000,
  });

  const { data: equipment } = useQuery({
    queryKey: ['equipment'],
    queryFn: fetchEquipmentTelemetry,
    refetchInterval: 30000,
  });

  const { data: workforce } = useQuery({
    queryKey: ['workforce', selectedShift],
    queryFn: () => fetchWorkforceDeficits(selectedShift),
    refetchInterval: 30000,
  });

  const { data: roster } = useQuery({
    queryKey: ['roster', selectedShift],
    queryFn: () => fetchRoster(selectedShift),
    refetchInterval: 30000,
  });

  // Dispense Mutation
  const dispenseMutation = useMutation({
    mutationFn: ({ sku, qty }: { sku: string; qty: number }) => dispenseMedication(sku, qty),
    onSuccess: (data) => {
      setDispenseResult(data);
      setDispenseError(null);
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
    },
    onError: (err: any) => {
      const msg = err.response?.data?.detail || err.message || 'Dispensing failed.';
      setDispenseError(msg);
      setDispenseResult(null);
    },
  });

  // Attendance Mutation
  const attendanceMutation = useMutation({
    mutationFn: ({ id, status, onDuty }: { id: string; status: string; onDuty: boolean }) =>
      updateStaffStatus(id, status, onDuty),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['roster'] });
      queryClient.invalidateQueries({ queryKey: ['workforce'] });
    },
  });

  const handleDispenseSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!dispenseItem) return;
    dispenseMutation.mutate({ sku: dispenseItem.sku_code, qty: dispenseQty });
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 bg-slate-900/90 border border-slate-800 p-4 rounded-2xl backdrop-blur">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Package className="w-5 h-5 text-indigo-400" />
            Resource Intelligence: Inventory, Equipment & Workforce
          </h1>
          <p className="text-xs text-slate-400 mt-0.5">
            Module 3 (Pharmacy FEFO & Oxygen Telemetry) + Module 4 (Clinical Staff Acuity Intelligence)
          </p>
        </div>
      </div>

      {/* ==================== 1. CRITICAL EQUIPMENT & OXYGEN TELEMETRY ==================== */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Ventilator Fleet */}
        <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Activity className="w-5 h-5 text-sky-400" />
              <h2 className="text-base font-bold text-white">Critical Care Ventilator Fleet</h2>
            </div>
            {equipment?.ventilators.critical_threshold_exceeded ? (
              <span className="px-2 py-0.5 text-xs font-bold rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/30">
                SURGE WARNING
              </span>
            ) : (
              <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-emerald-500/20 text-emerald-400">
                NOMINAL
              </span>
            )}
          </div>

          <div className="grid grid-cols-4 gap-2 pt-2 text-center">
            <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80">
              <div className="text-xs text-slate-400">Total Fleet</div>
              <div className="text-2xl font-extrabold text-white">{equipment?.ventilators.total ?? 0}</div>
            </div>
            <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80">
              <div className="text-xs text-sky-400">In Use</div>
              <div className="text-2xl font-extrabold text-sky-400">{equipment?.ventilators.in_use ?? 0}</div>
            </div>
            <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80">
              <div className="text-xs text-emerald-400">Available</div>
              <div className="text-2xl font-extrabold text-emerald-400">{equipment?.ventilators.available ?? 0}</div>
            </div>
            <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80">
              <div className="text-xs text-amber-400">Maintenance</div>
              <div className="text-2xl font-extrabold text-amber-400">{equipment?.ventilators.maintenance ?? 0}</div>
            </div>
          </div>

          {/* Utilization Progress Bar */}
          <div>
            <div className="flex justify-between text-xs text-slate-400 mb-1">
              <span>Fleet Utilization</span>
              <span className="font-bold text-white">{equipment?.ventilators.utilization_pct}%</span>
            </div>
            <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${
                  equipment?.ventilators.critical_threshold_exceeded ? 'bg-rose-500' : 'bg-sky-500'
                }`}
                style={{ width: `${equipment?.ventilators.utilization_pct ?? 0}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Oxygen Supply Telemetry */}
        <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Wind className="w-5 h-5 text-indigo-400" />
              <h2 className="text-base font-bold text-white">Liquid Medical Oxygen Reserve</h2>
            </div>
            {equipment?.oxygen_supply.low_supply_alert ? (
              <span className="px-2 py-0.5 text-xs font-bold rounded-full bg-rose-500/20 text-rose-400 border border-rose-500/30">
                LOW SUPPLY ALERT
              </span>
            ) : (
              <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-emerald-500/20 text-emerald-400">
                ADEQUATE
              </span>
            )}
          </div>

          <div className="grid grid-cols-3 gap-2 pt-2 text-center">
            <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80">
              <div className="text-xs text-slate-400">Current Volume</div>
              <div className="text-xl font-extrabold text-white">
                {equipment?.oxygen_supply.current_volume_liters.toLocaleString() ?? 0} L
              </div>
            </div>
            <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80">
              <div className="text-xs text-slate-400">Hourly Burn Rate</div>
              <div className="text-xl font-extrabold text-indigo-400">
                {equipment?.oxygen_supply.hourly_burn_rate_lph ?? 0} L/h
              </div>
            </div>
            <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80">
              <div className="text-xs text-emerald-400">Days of Supply</div>
              <div className="text-xl font-extrabold text-emerald-400">
                {equipment?.oxygen_supply.days_of_supply_remaining ?? 0} d
              </div>
            </div>
          </div>

          {/* Tank Level Bar */}
          <div>
            <div className="flex justify-between text-xs text-slate-400 mb-1">
              <span>Bulk Tank Level (Nominal: 10,000 L)</span>
              <span className="font-bold text-white">{equipment?.oxygen_supply.capacity_pct}%</span>
            </div>
            <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full bg-indigo-500 transition-all"
                style={{ width: `${equipment?.oxygen_supply.capacity_pct ?? 0}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* ==================== 2. SMART PHARMACY & FEFO DISPENSING ==================== */}
      <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Pill className="w-5 h-5 text-emerald-400" />
              <h2 className="text-base font-bold text-white">Module 3: Pharmacy Catalog & First Expiry, First Out (FEFO)</h2>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Automated batch tracking prioritizing nearest-expiry lots to prevent pharmaceutical waste
            </p>
          </div>

          {/* Category Filter Pills */}
          <div className="flex flex-wrap gap-1.5 bg-slate-950 p-1 rounded-xl border border-slate-800">
            {['ALL', 'Antibiotic', 'Critical_Care', 'Analgesic', 'Blood_PRBC'].map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
                  selectedCategory === cat
                    ? 'bg-emerald-500 text-slate-950 shadow-sm'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
                }`}
              >
                {cat.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        {/* Inventory Items Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider text-[11px]">
                <th className="py-3 px-4">SKU / Item Name</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Usable Stock</th>
                <th className="py-3 px-4">Reorder Threshold</th>
                <th className="py-3 px-4">Active Batches (FEFO)</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {loadingItems ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-500">Loading pharmaceutical stock...</td>
                </tr>
              ) : (
                items?.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3 px-4">
                      <div className="font-bold text-white text-sm">{item.generic_name}</div>
                      <div className="text-[11px] text-slate-500 font-mono">{item.sku_code}</div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 font-medium">
                        {item.category.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-extrabold text-white">{item.total_usable_stock}</span>
                        <span className="text-slate-500 text-[11px]">{item.unit_of_measure}s</span>
                      </div>
                      {item.reorder_required && (
                        <span className="inline-flex items-center gap-1 text-[10px] text-rose-400 font-bold mt-0.5">
                          <TrendingDown className="w-3 h-3" /> Reorder Triggered
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-slate-400">
                      {item.reorder_threshold} {item.unit_of_measure}s
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex flex-wrap gap-1">
                        {item.active_lots.map((lot, idx) => (
                          <span
                            key={lot.id}
                            className={`px-1.5 py-0.5 rounded text-[10px] font-mono border ${
                              idx === 0
                                ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400 font-bold'
                                : 'bg-slate-800/60 border-slate-700/60 text-slate-300'
                            }`}
                            title={`Expiry: ${lot.expiry_date} | Qty: ${lot.quantity_on_hand}`}
                          >
                            {idx === 0 ? '★ FEFO 1: ' : ''}{lot.lot_number} ({lot.quantity_on_hand})
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => {
                          setDispenseItem(item);
                          setDispenseQty(5);
                          setDispenseResult(null);
                          setDispenseError(null);
                        }}
                        className="px-3 py-1.5 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-semibold transition-all"
                      >
                        Dispense FEFO
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* ==================== 3. WORKFORCE & CLINICAL ACUITY ==================== */}
      <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Users className="w-5 h-5 text-sky-400" />
              <h2 className="text-base font-bold text-white">Module 4: Clinical Workforce & Acuity Coverage Intelligence</h2>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Dynamic staffing deficit analysis calculated by patient census and required clinical nurse-to-patient ratios
            </p>
          </div>

          {/* Shift Selector */}
          <div className="flex items-center gap-1.5 bg-slate-950 p-1 rounded-xl border border-slate-800">
            {['Morning', 'Evening', 'Night'].map((s) => (
              <button
                key={s}
                onClick={() => setSelectedShift(s)}
                className={`px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
                  selectedShift === s
                    ? 'bg-sky-500 text-slate-950 shadow-sm'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
                }`}
              >
                {s} Shift
              </button>
            ))}
          </div>
        </div>

        {/* Hospital-Wide Workforce Bar */}
        <div className="p-4 bg-slate-950/60 rounded-xl border border-slate-800/80 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <div className="text-xs text-slate-400">Total Shift Nursing Coverage</div>
            <div className="text-2xl font-extrabold text-white">
              {workforce?.hospital_coverage_pct}%
            </div>
          </div>
          <div className="flex items-center gap-6 text-xs">
            <div>
              <span className="text-slate-400 block">Required Nurses</span>
              <span className="font-bold text-slate-200 text-base">{workforce?.total_required_nurses}</span>
            </div>
            <div>
              <span className="text-slate-400 block">Present On-Duty</span>
              <span className="font-bold text-sky-400 text-base">{workforce?.total_present_nurses}</span>
            </div>
            <div>
              <span className="text-slate-400 block">Total Deficits</span>
              <span className={`font-bold text-base ${workforce && workforce.total_nurse_deficits > 0 ? 'text-rose-400' : 'text-emerald-400'}`}>
                {workforce?.total_nurse_deficits}
              </span>
            </div>
          </div>
        </div>

        {/* Ward Acuity Matrix */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {workforce?.ward_summaries.map((w) => (
            <div
              key={w.ward_id}
              className={`p-4 rounded-xl border space-y-2 ${
                w.has_deficit
                  ? 'bg-rose-950/20 border-rose-800/50'
                  : 'bg-slate-950/40 border-slate-800'
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-white text-sm">{w.ward_name}</span>
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                  {w.target_ratio}
                </span>
              </div>
              <div className="text-xs text-slate-400">
                Census: <span className="font-bold text-white">{w.patient_census} pts</span>
              </div>
              <div className="flex items-center justify-between pt-1 border-t border-slate-800/80 text-xs">
                <div>
                  <span className="text-slate-500 block text-[10px]">Required</span>
                  <span className="font-bold text-slate-200">{w.required_nurses}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px]">Present</span>
                  <span className="font-bold text-sky-400">{w.present_nurses}</span>
                </div>
                <div>
                  <span className="text-slate-500 block text-[10px]">Deficit</span>
                  <span className={`font-bold ${w.has_deficit ? 'text-rose-400' : 'text-emerald-400'}`}>
                    {w.nurse_deficit}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Staff Duty Roster Table */}
        <div className="space-y-3 pt-2">
          <h3 className="text-sm font-bold text-white">Current Shift Roster & Attendance Status</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px]">
                  <th className="py-2.5 px-4">Staff Member</th>
                  <th className="py-2.5 px-4">Role</th>
                  <th className="py-2.5 px-4">Shift</th>
                  <th className="py-2.5 px-4">Status</th>
                  <th className="py-2.5 px-4 text-right">Quick Toggle</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/40">
                {roster?.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-800/20">
                    <td className="py-2.5 px-4 font-semibold text-white">{r.staff_member_name}</td>
                    <td className="py-2.5 px-4 text-slate-400">{r.role}</td>
                    <td className="py-2.5 px-4 text-slate-400">{r.shift_name}</td>
                    <td className="py-2.5 px-4">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        r.status === 'Present'
                          ? 'bg-emerald-500/20 text-emerald-400'
                          : r.status === 'Absent'
                          ? 'bg-rose-500/20 text-rose-400'
                          : 'bg-slate-800 text-slate-300'
                      }`}>
                        {r.status}
                      </span>
                    </td>
                    <td className="py-2.5 px-4 text-right space-x-1.5">
                      <button
                        onClick={() => attendanceMutation.mutate({ id: r.id, status: 'Present', onDuty: true })}
                        className="px-2 py-0.5 rounded bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[10px]"
                      >
                        Present
                      </button>
                      <button
                        onClick={() => attendanceMutation.mutate({ id: r.id, status: 'Absent', onDuty: false })}
                        className="px-2 py-0.5 rounded bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 text-[10px]"
                      >
                        Absent
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* ==================== FEFO DISPENSE MODAL ==================== */}
      {dispenseItem && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 max-w-lg w-full rounded-2xl p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <div>
                <h3 className="text-base font-bold text-white">Execute FEFO Dispensation</h3>
                <p className="text-xs text-slate-400 font-mono">{dispenseItem.sku_code} — {dispenseItem.generic_name}</p>
              </div>
              <button
                onClick={() => setDispenseItem(null)}
                className="text-slate-400 hover:text-white text-lg font-bold"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleDispenseSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Requested Dispense Quantity ({dispenseItem.unit_of_measure}s):
                </label>
                <input
                  type="number"
                  min={1}
                  max={dispenseItem.total_usable_stock}
                  value={dispenseQty}
                  onChange={(e) => setDispenseQty(parseInt(e.target.value) || 1)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500"
                />
                <p className="text-[11px] text-slate-500 mt-1">
                  Usable stock on hand: <span className="font-bold text-white">{dispenseItem.total_usable_stock}</span>
                </p>
              </div>

              {dispenseError && (
                <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-xs text-rose-400 flex items-start gap-2">
                  <AlertTriangle className="w-4 h-4 flex-shrink-0 mt-0.5" />
                  <span>{dispenseError}</span>
                </div>
              )}

              {dispenseResult && (
                <div className="p-3.5 bg-emerald-500/10 border border-emerald-500/30 rounded-xl space-y-2 text-xs">
                  <div className="flex items-center gap-1.5 text-emerald-400 font-bold">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>FEFO Dispense Succeeded!</span>
                  </div>
                  <div className="space-y-1 text-slate-300">
                    <p>Allocations across expiring lots:</p>
                    {dispenseResult.dispensed_allocations.map((alloc) => (
                      <div key={alloc.lot_id} className="font-mono bg-slate-950/60 p-2 rounded border border-slate-800">
                        Lot: <span className="text-white font-bold">{alloc.lot_number}</span> | Deducted: <span className="text-emerald-400">{alloc.quantity_deducted}</span> | Remainder in Lot: {alloc.remaining_in_lot}
                      </div>
                    ))}
                    <p className="pt-1 text-[11px] text-slate-400">
                      Remaining Usable Stock for SKU: <span className="font-bold text-white">{dispenseResult.remaining_stock}</span>
                    </p>
                  </div>
                </div>
              )}

              <div className="flex justify-end gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setDispenseItem(null)}
                  className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-400 hover:text-white hover:bg-slate-800"
                >
                  Close
                </button>
                <button
                  type="submit"
                  disabled={dispenseMutation.isPending}
                  className="px-4 py-2 rounded-xl text-xs font-bold bg-emerald-500 text-slate-950 hover:bg-emerald-400 transition-all shadow-md"
                >
                  {dispenseMutation.isPending ? 'Dispensing...' : 'Confirm FEFO Dispensation'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
