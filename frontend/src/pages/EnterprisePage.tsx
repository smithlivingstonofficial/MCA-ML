import React, { useState, useEffect } from 'react';
import {
  KeyRound,
  FileText,
  Share2,
  Download,
  CheckCircle,
  Copy,
  Layers,
  Clock,
  UserCheck
} from 'lucide-react';
import {
  fetchRoles,
  login,
  fetchAuditLogs,
  fetchExecutiveBrief,
  fetchFHIRBeds,
  fetchFHIRHospitalBundle,
  ingestFHIRBundle
} from '../services/api';
import {
  RoleInfo,
  UserProfileResponse,
  AuditLogItem,
  ExecutiveBriefResponse
} from '../types';

export const EnterprisePage: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = useState<'AUTH' | 'FHIR' | 'AUDIT' | 'REPORTS'>('AUTH');
  const [roles, setRoles] = useState<RoleInfo[]>([]);
  const [currentUser, setCurrentUser] = useState<UserProfileResponse | null>(null);
  const [activeToken, setActiveToken] = useState<string>('');
  const [authMessage, setAuthMessage] = useState<string>('');
  const [isLoadingAuth, setIsLoadingAuth] = useState<boolean>(false);

  // FHIR State
  const [fhirData, setFhirData] = useState<any>(null);
  const [fhirMode, setFhirMode] = useState<'BEDS' | 'HOSPITAL' | 'INGEST'>('BEDS');
  const [copied, setCopied] = useState<boolean>(false);
  const [ingestStatus, setIngestStatus] = useState<string>('');
  const [isIngesting, setIsIngesting] = useState<boolean>(false);

  // Audit State
  const [auditLogs, setAuditLogs] = useState<AuditLogItem[]>([]);
  const [auditTotal, setAuditTotal] = useState<number>(0);
  const [filterModule, setFilterModule] = useState<string>('ALL');
  const [filterAction, setFilterAction] = useState<string>('ALL');
  const [isLoadingAudit, setIsLoadingAudit] = useState<boolean>(false);

  // Reports State
  const [brief, setBrief] = useState<ExecutiveBriefResponse | null>(null);

  // Initial Load
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [rolesData, briefData] = await Promise.all([
        fetchRoles(),
        fetchExecutiveBrief()
      ]);
      setRoles(rolesData);
      setBrief(briefData);

      // Default login as Admin for seamless demonstration
      handleRoleSwitch('admin', 'admin123');
    } catch (err) {
      console.error('Failed to load initial enterprise data:', err);
    }
  };

  const handleRoleSwitch = async (username: string, password: string) => {
    setIsLoadingAuth(true);
    try {
      const tokenResp = await login(username, password);
      setCurrentUser(tokenResp.user);
      setActiveToken(tokenResp.access_token);
      setAuthMessage(`Switched active session to: ${tokenResp.user.full_name} (${tokenResp.user.role})`);
      setTimeout(() => setAuthMessage(''), 4000);
    } catch (err) {
      console.error('Login error:', err);
      setAuthMessage('Authentication failed.');
    } finally {
      setIsLoadingAuth(false);
    }
  };

  // Load FHIR on demand
  useEffect(() => {
    if (activeSubTab === 'FHIR') {
      loadFhirPreview();
    }
  }, [activeSubTab, fhirMode]);

  const loadFhirPreview = async () => {
    try {
      if (fhirMode === 'BEDS') {
        const bedsBundle = await fetchFHIRBeds();
        setFhirData(bedsBundle);
      } else if (fhirMode === 'HOSPITAL') {
        const hospBundle = await fetchFHIRHospitalBundle(15);
        setFhirData(hospBundle);
      }
    } catch (err) {
      console.error('Failed to load FHIR bundle:', err);
    }
  };

  // Load Audit Logs on demand
  useEffect(() => {
    if (activeSubTab === 'AUDIT') {
      loadAuditEvents();
    }
  }, [activeSubTab, filterModule, filterAction]);

  const loadAuditEvents = async () => {
    setIsLoadingAudit(true);
    try {
      const logsResp = await fetchAuditLogs(filterModule, filterAction, undefined, 50);
      setAuditLogs(logsResp.events);
      setAuditTotal(logsResp.total_events);
    } catch (err) {
      console.error('Failed to load audit logs:', err);
    } finally {
      setIsLoadingAudit(false);
    }
  };

  const handleCopyJson = () => {
    if (fhirData) {
      navigator.clipboard.writeText(JSON.stringify(fhirData, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleTestFhirIngest = async () => {
    setIsIngesting(true);
    setIngestStatus('');
    try {
      const sampleBundle = {
        resourceType: 'Bundle',
        type: 'collection',
        entry: [
          {
            fullUrl: 'urn:uuid:INGESTED-PATIENT-01',
            resource: {
              resourceType: 'Encounter',
              id: `FHIR-DEMO-${Date.now().toString().slice(-4)}`,
              identifier: [{ value: `MRN-EXT-${Date.now().toString().slice(-4)}` }],
              status: 'in-progress',
              class: { code: 'EMER', display: 'Emergency Intake via HL7 FHIR' },
              period: { start: new Date().toISOString() }
            }
          }
        ]
      };

      const res = await ingestFHIRBundle(sampleBundle);
      setIngestStatus(`Success: ${res.message}`);
      loadAuditEvents();
    } catch (err: any) {
      setIngestStatus(`Error: ${err?.message || 'Failed to ingest bundle.'}`);
    } finally {
      setIsIngesting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Banner */}
      <div className="bg-slate-900/90 border-l-4 border-emerald-500 rounded-r-xl p-4 text-xs text-slate-300 flex items-start justify-between shadow-lg">
        <div className="space-y-1">
          <div className="flex items-center gap-2 font-bold text-emerald-400 text-sm">
            <span>🔐</span>
            <span>Phase 6: Enterprise Interoperability, Clinical Security & Regulatory Compliance</span>
          </div>
          <p>
            Standardized <strong className="text-white">HL7 FHIR Release 4</strong> data exchange with external EHRs,
            cryptographic HMAC-SHA256 session enforcement, and immutable regulatory audit logs.
          </p>
        </div>
        <div className="hidden md:flex items-center gap-2 bg-slate-950 px-3 py-1.5 rounded border border-slate-800 font-mono text-[11px] text-slate-400">
          <span>Standards: HL7 FHIR R4</span>
          <span>•</span>
          <span>Security: RBAC</span>
        </div>
      </div>

      {/* Navigation Sub-Tabs */}
      <div className="flex border-b border-slate-800 gap-4">
        <button
          onClick={() => setActiveSubTab('AUTH')}
          className={`pb-3 text-sm font-semibold transition-colors flex items-center gap-2 ${
            activeSubTab === 'AUTH'
              ? 'text-emerald-400 border-b-2 border-emerald-500'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <KeyRound className="w-4 h-4" />
          <span>Role-Based Access Control</span>
        </button>

        <button
          onClick={() => setActiveSubTab('FHIR')}
          className={`pb-3 text-sm font-semibold transition-colors flex items-center gap-2 ${
            activeSubTab === 'FHIR'
              ? 'text-emerald-400 border-b-2 border-emerald-500'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Share2 className="w-4 h-4" />
          <span>HL7 FHIR R4 Console</span>
        </button>

        <button
          onClick={() => setActiveSubTab('AUDIT')}
          className={`pb-3 text-sm font-semibold transition-colors flex items-center gap-2 ${
            activeSubTab === 'AUDIT'
              ? 'text-emerald-400 border-b-2 border-emerald-500'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Clock className="w-4 h-4" />
          <span>Compliance Audit Trail</span>
        </button>

        <button
          onClick={() => setActiveSubTab('REPORTS')}
          className={`pb-3 text-sm font-semibold transition-colors flex items-center gap-2 ${
            activeSubTab === 'REPORTS'
              ? 'text-emerald-400 border-b-2 border-emerald-500'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>Executive Reports & CSVs</span>
        </button>
      </div>

      {/* Tab 1: RBAC & Role Switcher */}
      {activeSubTab === 'AUTH' && (
        <div className="space-y-6">
          {/* Active Session Status Bar */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-lg">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 font-bold">
                <UserCheck className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-bold text-white text-sm">
                    {currentUser?.full_name || 'Loading user...'}
                  </span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-emerald-950 text-emerald-400 border border-emerald-800">
                    {currentUser?.role || 'HOSPITAL_ADMIN'}
                  </span>
                </div>
                <p className="text-xs text-slate-400 mt-0.5">
                  Department: {currentUser?.department || 'Operations Intelligence'}
                </p>
              </div>
            </div>

            <div className="text-right font-mono text-[11px] text-slate-400">
              <p>Cryptographic Bearer Token: Active</p>
              <p className="text-slate-500 truncate max-w-xs">{activeToken.slice(0, 32)}...</p>
            </div>
          </div>

          {authMessage && (
            <div className="bg-emerald-950/40 border border-emerald-800 text-emerald-300 px-4 py-2 rounded-lg text-xs flex items-center gap-2">
              <CheckCircle className="w-4 h-4" />
              <span>{authMessage}</span>
            </div>
          )}

          {/* Role Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {roles.map((r) => {
              const isActive = currentUser?.role === r.role_key;
              const [user, pwd] = r.demo_username.split(' (Password: ');
              const cleanPwd = pwd ? pwd.replace(')', '') : 'admin123';

              return (
                <div
                  key={r.role_key}
                  className={`bg-slate-900 border rounded-xl p-5 flex flex-col justify-between transition-all ${
                    isActive
                      ? 'border-emerald-500 ring-1 ring-emerald-500/50 shadow-emerald-950/20 shadow-lg'
                      : 'border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
                        {r.role_key}
                      </span>
                      {isActive && (
                        <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                      )}
                    </div>

                    <h3 className="font-bold text-white text-sm">{r.title}</h3>
                    <p className="text-xs text-slate-400 leading-relaxed">{r.description}</p>

                    <div className="space-y-1.5 pt-2">
                      <p className="text-[10px] font-semibold text-slate-500 uppercase">Permissions</p>
                      <div className="flex flex-wrap gap-1">
                        {r.permissions.map((p) => (
                          <span
                            key={p}
                            className="px-1.5 py-0.5 rounded text-[9px] bg-slate-800 text-slate-300 font-mono"
                          >
                            {p}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="pt-5">
                    <button
                      onClick={() => handleRoleSwitch(user.trim(), cleanPwd.trim())}
                      disabled={isLoadingAuth || isActive}
                      className={`w-full py-2 rounded-lg text-xs font-semibold transition-all ${
                        isActive
                          ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-500/30 cursor-default'
                          : 'bg-slate-800 hover:bg-emerald-600 text-slate-300 hover:text-white'
                      }`}
                    >
                      {isActive ? '✓ Active Role' : `Switch to ${user.trim()}`}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Tab 2: HL7 FHIR R4 Console */}
      {activeSubTab === 'FHIR' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setFhirMode('BEDS')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold ${
                    fhirMode === 'BEDS' ? 'bg-emerald-600 text-white' : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  Bed Locations (Location Bundle)
                </button>
                <button
                  onClick={() => setFhirMode('HOSPITAL')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold ${
                    fhirMode === 'HOSPITAL' ? 'bg-emerald-600 text-white' : 'bg-slate-800 text-slate-400'
                  }`}
                >
                  Complete Hospital Collection
                </button>
              </div>

              <button
                onClick={handleCopyJson}
                className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs rounded-lg transition-colors"
              >
                <Copy className="w-3.5 h-3.5" />
                <span>{copied ? 'Copied!' : 'Copy FHIR JSON'}</span>
              </button>
            </div>

            {/* JSON Viewer */}
            <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 font-mono text-[11px] text-emerald-400/90 max-h-[500px] overflow-y-auto shadow-inner">
              <pre>{fhirData ? JSON.stringify(fhirData, null, 2) : 'Loading FHIR R4 standard payload...'}</pre>
            </div>
          </div>

          {/* Right: FHIR Ingestion Test Rig */}
          <div className="space-y-4">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4 shadow-lg">
              <div className="flex items-center gap-2 text-white font-bold text-sm">
                <Layers className="w-4 h-4 text-emerald-400" />
                <span>External EHR Ingestion Test Rig</span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Test inbound interoperability by injecting an HL7 FHIR R4 Bundle containing real-time Emergency
                Department encounter dispatches.
              </p>

              <div className="bg-slate-950 p-3 rounded-lg border border-slate-800 font-mono text-[10px] text-slate-400 space-y-1">
                <p className="text-emerald-400">Payload: HL7 FHIR R4 Encounter</p>
                <p>Status: in-progress</p>
                <p>Class: EMER (Emergency Department)</p>
                <p>Standard: urn:oid:hospital:patient-pseudonym</p>
              </div>

              <button
                onClick={handleTestFhirIngest}
                disabled={isIngesting}
                className="w-full py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                {isIngesting ? 'Ingesting via FHIR...' : '🚀 Ingest Sample FHIR Bundle'}
              </button>

              {ingestStatus && (
                <div
                  className={`p-3 rounded-lg text-xs leading-snug ${
                    ingestStatus.startsWith('Success')
                      ? 'bg-emerald-950/40 border border-emerald-800 text-emerald-300'
                      : 'bg-rose-950/40 border border-rose-800 text-rose-300'
                  }`}
                >
                  {ingestStatus}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Compliance Audit Trail */}
      {activeSubTab === 'AUDIT' && (
        <div className="space-y-4">
          {/* Audit Filter Bar */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-wrap items-center justify-between gap-3 shadow-lg">
            <div className="flex items-center gap-3">
              <span className="text-xs text-slate-400">Module:</span>
              <select
                value={filterModule}
                onChange={(e) => setFilterModule(e.target.value)}
                className="bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-lg px-2.5 py-1.5 focus:outline-none"
              >
                <option value="ALL">All Modules</option>
                <option value="Module 1">Module 1 (Patient Flow)</option>
                <option value="Module 2">Module 2 (Beds)</option>
                <option value="Module 3">Module 3 (Inventory)</option>
                <option value="Module 5">Module 5 (PuLP Optimization)</option>
                <option value="Module 6">Module 6 (Continuity)</option>
                <option value="Module 7">Module 7 (Governance)</option>
              </select>

              <span className="text-xs text-slate-400">Action:</span>
              <select
                value={filterAction}
                onChange={(e) => setFilterAction(e.target.value)}
                className="bg-slate-800 border border-slate-700 text-slate-200 text-xs rounded-lg px-2.5 py-1.5 focus:outline-none"
              >
                <option value="ALL">All Actions</option>
                <option value="BED_STATE_CHANGE">BED_STATE_CHANGE</option>
                <option value="OPTIMIZATION_EXECUTED">OPTIMIZATION_EXECUTED</option>
                <option value="MEDICATION_DISPENSED">MEDICATION_DISPENSED</option>
                <option value="CONTINUITY_EVALUATION">CONTINUITY_EVALUATION</option>
                <option value="FHIR_BUNDLE_EXPORT">FHIR_BUNDLE_EXPORT</option>
                <option value="FHIR_BUNDLE_INGESTION">FHIR_BUNDLE_INGESTION</option>
              </select>
            </div>

            <span className="text-xs text-slate-400 font-mono">
              {auditTotal} Compliance Events Recorded
            </span>
          </div>

          {/* Audit Table */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-300">
                <thead className="bg-slate-800/60 uppercase tracking-wider text-[11px] text-slate-400">
                  <tr>
                    <th className="py-3 px-4">Timestamp</th>
                    <th className="py-3 px-4">Actor</th>
                    <th className="py-3 px-4">Role</th>
                    <th className="py-3 px-4">Module</th>
                    <th className="py-3 px-4">Action Code</th>
                    <th className="py-3 px-4">Resource</th>
                    <th className="py-3 px-4">Audit Details</th>
                    <th className="py-3 px-4 text-right">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800">
                  {isLoadingAudit ? (
                    <tr>
                      <td colSpan={8} className="py-8 text-center text-slate-500">
                        Querying immutable audit logs...
                      </td>
                    </tr>
                  ) : auditLogs.length === 0 ? (
                    <tr>
                      <td colSpan={8} className="py-8 text-center text-slate-500">
                        No audit events matching current filter.
                      </td>
                    </tr>
                  ) : (
                    auditLogs.map((log) => (
                      <tr key={log.id} className="hover:bg-slate-800/40 transition-colors">
                        <td className="py-3 px-4 font-mono text-[11px] text-slate-400">
                          {new Date(log.timestamp).toLocaleTimeString([], {
                            hour: '2-digit',
                            minute: '2-digit',
                            second: '2-digit'
                          })}
                        </td>
                        <td className="py-3 px-4 font-medium text-white">{log.actor_id}</td>
                        <td className="py-3 px-4">
                          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                            {log.actor_role}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-slate-400">{log.module}</td>
                        <td className="py-3 px-4 font-mono text-emerald-400 font-bold">{log.action}</td>
                        <td className="py-3 px-4 font-mono text-[11px] text-slate-400">
                          {log.resource_id || '--'}
                        </td>
                        <td className="py-3 px-4 max-w-xs truncate text-slate-300" title={log.details}>
                          {log.details}
                        </td>
                        <td className="py-3 px-4 text-right">
                          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">
                            {log.status}
                          </span>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Tab 4: Executive Reports & CSV Station */}
      {activeSubTab === 'REPORTS' && (
        <div className="space-y-6">
          {brief && (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-5 shadow-lg">
              <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                <div>
                  <h3 className="text-base font-bold text-white">{brief.hospital_name}</h3>
                  <p className="text-xs text-slate-400">
                    Consolidated 24-Hour Operational Briefing Report • Fresh as of {new Date(brief.generated_at).toLocaleTimeString()}
                  </p>
                </div>
                <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-950 text-emerald-400 border border-emerald-800">
                  Governance: {brief.model_governance_status}
                </span>
              </div>

              {/* KPI Matrix */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                  <p className="text-xs text-slate-400 uppercase tracking-wider">Physical Occupancy</p>
                  <p className="text-2xl font-bold text-white mt-1">{brief.hospital_occupancy_pct}%</p>
                  <p className="text-[11px] text-slate-500">{brief.total_physical_beds} total beds</p>
                </div>

                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                  <p className="text-xs text-slate-400 uppercase tracking-wider">Staffed Occupancy</p>
                  <p className="text-2xl font-bold text-indigo-400 mt-1">{brief.staffed_occupancy_pct}%</p>
                  <p className="text-[11px] text-slate-500">{brief.total_staffed_beds} staffed ceiling</p>
                </div>

                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                  <p className="text-xs text-slate-400 uppercase tracking-wider">24h ED Inflow</p>
                  <p className="text-2xl font-bold text-sky-400 mt-1">{brief.ed_arrivals_past_24h}</p>
                  <p className="text-[11px] text-slate-500">Forecast: {brief.ed_forecast_next_24h}</p>
                </div>

                <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                  <p className="text-xs text-slate-400 uppercase tracking-wider">Oxygen Reserves</p>
                  <p className="text-2xl font-bold text-emerald-400 mt-1">{brief.oxygen_days_remaining}d</p>
                  <p className="text-[11px] text-slate-500">Vent: {brief.ventilator_utilization_pct}%</p>
                </div>
              </div>
            </div>
          )}

          {/* Download Center */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <a
              href="/api/v1/reports/readmission-cohort.csv"
              download
              className="bg-slate-900 border border-slate-800 hover:border-emerald-500/50 p-5 rounded-xl block space-y-3 transition-all group shadow-md"
            >
              <div className="w-10 h-10 rounded-xl bg-purple-500/10 text-purple-400 flex items-center justify-center group-hover:bg-purple-500/20">
                <Download className="w-5 h-5" />
              </div>
              <h4 className="font-bold text-white text-sm">Download Readmission Cohort (.CSV)</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Export evaluated high-risk patient encounters, readmission scores, no-show probabilities, and care
                coordination recommendations.
              </p>
            </a>

            <a
              href="/api/v1/reports/bed-occupancy.csv"
              download
              className="bg-slate-900 border border-slate-800 hover:border-emerald-500/50 p-5 rounded-xl block space-y-3 transition-all group shadow-md"
            >
              <div className="w-10 h-10 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center group-hover:bg-indigo-500/20">
                <Download className="w-5 h-5" />
              </div>
              <h4 className="font-bold text-white text-sm">Download Ward Bed Census (.CSV)</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Departmental breakdown of physical beds, ready beds, on-duty nurse counts, staffed ceilings, and
                staffing deficits.
              </p>
            </a>

            <a
              href="/api/v1/fhir/export/hospital-bundle"
              target="_blank"
              rel="noreferrer"
              className="bg-slate-900 border border-slate-800 hover:border-emerald-500/50 p-5 rounded-xl block space-y-3 transition-all group shadow-md"
            >
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center group-hover:bg-emerald-500/20">
                <Download className="w-5 h-5" />
              </div>
              <h4 className="font-bold text-white text-sm">Export Full HL7 FHIR Bundle (.JSON)</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                Download the complete hospital operational model formatted as a compliant HL7 FHIR Release 4
                Collection Bundle.
              </p>
            </a>
          </div>
        </div>
      )}
    </div>
  );
};
