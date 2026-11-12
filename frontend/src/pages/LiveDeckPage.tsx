import React, { useState, useEffect, useRef } from 'react';
import {
  Activity,
  AlertTriangle,
  Zap,
  Radio,
  RefreshCw,
  Sliders,
  CheckCircle2,
  Clock,
  Sparkles,
  Send,
  Play
} from 'lucide-react';
import {
  fetchOperationalAnomalies,
  fetchCopilotRecommendations,
  dispatchCopilotAction,
  triggerLiveSimulationEvent
} from '../services/api';
import {
  AnomalyDetectionResponse,
  CopilotRecommendationsResponse,
  WebSocketEventMessage
} from '../types';

export const LiveDeckPage: React.FC = () => {
  const [activeSubTab, setActiveSubTab] = useState<'RADAR' | 'COPILOT' | 'TICKER' | 'SIMULATOR'>('RADAR');
  const [anomalyData, setAnomalyData] = useState<AnomalyDetectionResponse | null>(null);
  const [copilotData, setCopilotData] = useState<CopilotRecommendationsResponse | null>(null);
  const [liveEvents, setLiveEvents] = useState<WebSocketEventMessage[]>([]);
  const [isWsConnected, setIsWsConnected] = useState<boolean>(false);
  const [filterSeverity, setFilterSeverity] = useState<string>('ALL');
  const [actionNotes, setActionNotes] = useState<Record<string, string>>({});
  const [dispatchStatus, setDispatchStatus] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [pingLatency, setPingLatency] = useState<number | null>(null);
  const [simMessage, setSimMessage] = useState<string>('');

  const wsRef = useRef<WebSocket | null>(null);
  const pingTimestampRef = useRef<number>(0);

  // Initialize WebSocket connection and data polling
  useEffect(() => {
    loadLiveIntelligence();
    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${protocol}//${window.location.host}/ws/live-stream`;

      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsWsConnected(true);
      };

      ws.onmessage = (event) => {
        try {
          const raw = JSON.parse(event.data);
          if (raw.event_type === 'PONG') {
            const rtt = Date.now() - pingTimestampRef.current;
            setPingLatency(rtt);
            return;
          }

          const newEvt: WebSocketEventMessage = {
            event_id: raw.event_id || `evt-${Date.now()}`,
            event_type: raw.event_type || 'SYSTEM_TELEMETRY',
            timestamp: raw.timestamp || new Date().toISOString(),
            module: raw.module || 'HOSPITAL_OPERATIONS',
            severity: raw.severity || 'INFO',
            message: raw.message || JSON.stringify(raw),
            payload: raw.payload
          };

          setLiveEvents((prev) => [newEvt, ...prev.slice(0, 49)]);

          // If a new anomaly or copilot event is detected, refresh telemetry
          if (newEvt.event_type.includes('ANOMALY') || newEvt.event_type.includes('COPILOT') || newEvt.event_type.includes('SIMULATION')) {
            loadLiveIntelligence();
          }
        } catch {
          // Non-JSON ping
        }
      };

      ws.onclose = () => {
        setIsWsConnected(false);
      };

      ws.onerror = () => {
        setIsWsConnected(false);
      };
    } catch {
      setIsWsConnected(false);
    }
  };

  const sendPing = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      pingTimestampRef.current = Date.now();
      wsRef.current.send('ping');
    }
  };

  const loadLiveIntelligence = async () => {
    setIsLoading(true);
    try {
      const [anomalies, recs] = await Promise.all([
        fetchOperationalAnomalies(),
        fetchCopilotRecommendations()
      ]);
      setAnomalyData(anomalies);
      setCopilotData(recs);
    } catch (err) {
      console.error('Failed to load live intelligence:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDispatchAction = async (recId: string) => {
    try {
      const note = actionNotes[recId] || 'Authorized via AI Operations Copilot Deck';
      setDispatchStatus((prev) => ({ ...prev, [recId]: 'DISPATCHING...' }));
      const res = await dispatchCopilotAction(recId, note);
      setDispatchStatus((prev) => ({ ...prev, [recId]: `SUCCESS: ${res.status}` }));

      // Refresh copilot list
      const updatedRecs = await fetchCopilotRecommendations();
      setCopilotData(updatedRecs);
    } catch {
      setDispatchStatus((prev) => ({ ...prev, [recId]: 'ERROR DISPATCHING' }));
    }
  };

  const handleTriggerSim = async (
    eventType: string,
    message: string,
    severity: 'INFO' | 'WARNING' | 'CRITICAL',
    payload?: Record<string, any>
  ) => {
    setSimMessage(`Triggering ${eventType}...`);
    try {
      await triggerLiveSimulationEvent({
        event_type: eventType,
        message,
        module: 'SIMULATOR',
        severity,
        payload
      });
      setSimMessage(`Dispatched: ${message}`);
      setTimeout(() => setSimMessage(''), 4000);
      await loadLiveIntelligence();
    } catch (e: any) {
      setSimMessage(`Failed to trigger simulation: ${e.message}`);
    }
  };

  const filteredEvents = liveEvents.filter((ev) => {
    if (filterSeverity === 'ALL') return true;
    return ev.severity === filterSeverity;
  });

  const healthScore = anomalyData?.overall_operational_health_score ?? 85;

  return (
    <div className="space-y-6">
      {/* Top Header Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-xl relative overflow-hidden">
        <div className="absolute top-0 right-0 p-4 opacity-10 pointer-events-none">
          <Activity className="w-64 h-64 text-indigo-400" />
        </div>

        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 relative z-10">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                Phase 7 Real-Time Architecture
              </span>
              <div className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border bg-slate-800">
                <span
                  className={`w-2 h-2 rounded-full ${
                    isWsConnected ? 'bg-emerald-400 animate-pulse' : 'bg-rose-500'
                  }`}
                />
                <span className={isWsConnected ? 'text-emerald-400' : 'text-rose-400'}>
                  {isWsConnected ? 'LIVE STREAM' : 'DISCONNECTED'}
                </span>
                {pingLatency !== null && (
                  <span className="text-slate-400 ml-1">({pingLatency}ms)</span>
                )}
              </div>
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">
              Live Operations Command Deck & AI Copilot
            </h1>
            <p className="text-slate-400 text-sm mt-0.5">
              Event-driven real-time bi-directional streaming, multi-vector anomaly detection & human-supervised mitigation dispatch
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={sendPing}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs rounded-lg border border-slate-700 transition"
              title="Ping WebSocket server"
            >
              <Radio className="w-3.5 h-3.5 text-indigo-400" />
              Ping WS
            </button>
            <button
              onClick={loadLiveIntelligence}
              disabled={isLoading}
              className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium rounded-lg shadow-lg shadow-indigo-600/30 transition disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
              Re-Scan Radar
            </button>
          </div>
        </div>

        {/* Global Telemetry KPI Strip */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-5 border-t border-slate-800/80">
          <div className="bg-slate-800/60 p-3 rounded-lg border border-slate-700/50">
            <div className="text-xs font-medium text-slate-400 flex items-center justify-between">
              Operational Health Index
              <Activity className="w-3.5 h-3.5 text-indigo-400" />
            </div>
            <div className="flex items-baseline gap-2 mt-1">
              <span
                className={`text-2xl font-bold ${
                  healthScore >= 80
                    ? 'text-emerald-400'
                    : healthScore >= 60
                    ? 'text-amber-400'
                    : 'text-rose-400'
                }`}
              >
                {healthScore}
              </span>
              <span className="text-xs text-slate-500">/ 100</span>
            </div>
            <div className="w-full bg-slate-700 h-1.5 rounded-full mt-2 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-500 ${
                  healthScore >= 80
                    ? 'bg-emerald-500'
                    : healthScore >= 60
                    ? 'bg-amber-500'
                    : 'bg-rose-500'
                }`}
                style={{ width: `${healthScore}%` }}
              />
            </div>
          </div>

          <div className="bg-slate-800/60 p-3 rounded-lg border border-slate-700/50">
            <div className="text-xs font-medium text-slate-400 flex items-center justify-between">
              Active Anomalies
              <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
            </div>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-2xl font-bold text-white">
                {anomalyData?.anomalies_detected_count ?? 0}
              </span>
              <span className="text-xs text-rose-400">
                ({anomalyData?.critical_count ?? 0} Critical)
              </span>
            </div>
            <div className="text-xs text-slate-400 mt-2 truncate">
              {anomalyData?.warning_count ?? 0} warnings monitored
            </div>
          </div>

          <div className="bg-slate-800/60 p-3 rounded-lg border border-slate-700/50">
            <div className="text-xs font-medium text-slate-400 flex items-center justify-between">
              Copilot Mitigations
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            </div>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-2xl font-bold text-indigo-400">
                {copilotData?.total_recommendations ?? 0}
              </span>
              <span className="text-xs text-amber-400">
                ({copilotData?.immediate_actions_count ?? 0} Urgent)
              </span>
            </div>
            <div className="text-xs text-slate-400 mt-2">Human-supervised dispatch</div>
          </div>

          <div className="bg-slate-800/60 p-3 rounded-lg border border-slate-700/50">
            <div className="text-xs font-medium text-slate-400 flex items-center justify-between">
              Live Stream Buffer
              <Radio className="w-3.5 h-3.5 text-emerald-400" />
            </div>
            <div className="flex items-baseline gap-2 mt-1">
              <span className="text-2xl font-bold text-white">{liveEvents.length}</span>
              <span className="text-xs text-slate-400">events logged</span>
            </div>
            <div className="text-xs text-emerald-400 mt-2 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Bi-directional pub/sub active
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Sub-Tabs */}
      <div className="flex border-b border-slate-800 gap-2">
        <button
          onClick={() => setActiveSubTab('RADAR')}
          className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition ${
            activeSubTab === 'RADAR'
              ? 'border-indigo-500 text-indigo-400 bg-indigo-500/10'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Activity className="w-4 h-4" />
          Anomaly Detection Radar
          {anomalyData && anomalyData.anomalies_detected_count > 0 && (
            <span className="px-1.5 py-0.5 text-xs rounded-full bg-rose-500 text-white font-bold">
              {anomalyData.anomalies_detected_count}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveSubTab('COPILOT')}
          className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition ${
            activeSubTab === 'COPILOT'
              ? 'border-indigo-500 text-indigo-400 bg-indigo-500/10'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Sparkles className="w-4 h-4" />
          AI Operations Copilot
          {copilotData && copilotData.immediate_actions_count > 0 && (
            <span className="px-1.5 py-0.5 text-xs rounded-full bg-amber-500 text-slate-950 font-bold">
              {copilotData.immediate_actions_count}
            </span>
          )}
        </button>

        <button
          onClick={() => setActiveSubTab('TICKER')}
          className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition ${
            activeSubTab === 'TICKER'
              ? 'border-indigo-500 text-indigo-400 bg-indigo-500/10'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Radio className="w-4 h-4" />
          Live Event Ticker
          <span className="px-1.5 py-0.5 text-xs rounded-full bg-slate-800 text-slate-300">
            {liveEvents.length}
          </span>
        </button>

        <button
          onClick={() => setActiveSubTab('SIMULATOR')}
          className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition ${
            activeSubTab === 'SIMULATOR'
              ? 'border-indigo-500 text-indigo-400 bg-indigo-500/10'
              : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          <Sliders className="w-4 h-4" />
          Real-Time Chaos Simulator
        </button>
      </div>

      {/* SUB-TAB 1: RADAR (Operational Anomaly Detection) */}
      {activeSubTab === 'RADAR' && (
        <div className="space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div>
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <Activity className="w-5 h-5 text-indigo-400" />
                  Statistical Z-Score & CUSUM Operational Anomaly Radar
                </h2>
                <p className="text-slate-400 text-xs mt-1">
                  Evaluates continuous distribution shifts in ED triage wait times, uncleaned bed turnaround lag, and biomedical liquid oxygen reserves.
                </p>
              </div>
              <div className="text-right">
                <span className="text-xs text-slate-400">
                  Last Evaluated: {anomalyData ? new Date(anomalyData.evaluated_at).toLocaleTimeString() : 'Pending'}
                </span>
              </div>
            </div>

            {/* Diagnostic Banner */}
            <div className="mt-4 p-3 bg-slate-800/80 rounded-lg border border-slate-700 text-xs text-slate-300 flex items-center justify-between">
              <span>{anomalyData?.diagnostic_summary || 'No active alerts detected. Hospital operating within baseline.'}</span>
              <span className="text-slate-400 text-2xs">Z-Threshold: ±2.50σ</span>
            </div>
          </div>

          {/* Anomaly Cards List */}
          {anomalyData && anomalyData.anomalies.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {anomalyData.anomalies.map((a) => (
                <div
                  key={a.anomaly_id}
                  className={`p-5 rounded-xl border bg-slate-900 transition-all ${
                    a.severity === 'CRITICAL'
                      ? 'border-rose-500/50 shadow-lg shadow-rose-950/20'
                      : a.severity === 'WARNING'
                      ? 'border-amber-500/50 shadow-lg shadow-amber-950/20'
                      : 'border-slate-800'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-2">
                      {a.severity === 'CRITICAL' ? (
                        <div className="p-2 rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/20">
                          <AlertTriangle className="w-5 h-5" />
                        </div>
                      ) : (
                        <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
                          <AlertTriangle className="w-5 h-5" />
                        </div>
                      )}
                      <div>
                        <span className="text-2xs font-bold uppercase tracking-wider text-slate-400">
                          {a.category} • {a.target_entity}
                        </span>
                        <h3 className="text-base font-semibold text-white mt-0.5">{a.title}</h3>
                      </div>
                    </div>

                    <span
                      className={`px-2 py-0.5 rounded text-xs font-bold ${
                        a.severity === 'CRITICAL'
                          ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                          : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                      }`}
                    >
                      {a.severity}
                    </span>
                  </div>

                  {/* Quantitative Metrics Meter */}
                  <div className="grid grid-cols-3 gap-2 mt-4 pt-3 border-t border-slate-800/80 text-xs">
                    <div className="bg-slate-800/40 p-2 rounded">
                      <div className="text-slate-400 text-2xs">Detected Value</div>
                      <div className="font-semibold text-white mt-0.5">{a.detected_value}</div>
                    </div>
                    <div className="bg-slate-800/40 p-2 rounded">
                      <div className="text-slate-400 text-2xs">Expected Baseline</div>
                      <div className="font-semibold text-slate-300 mt-0.5">{a.expected_baseline}</div>
                    </div>
                    <div className="bg-slate-800/40 p-2 rounded">
                      <div className="text-slate-400 text-2xs">Statistical Z-Score</div>
                      <div
                        className={`font-semibold mt-0.5 ${
                          Math.abs(a.z_score) >= 3.0 ? 'text-rose-400' : 'text-amber-400'
                        }`}
                      >
                        {a.z_score >= 0 ? `+${a.z_score}` : a.z_score}σ
                      </div>
                    </div>
                  </div>

                  {/* Root Cause Analysis */}
                  <div className="mt-3 text-xs bg-slate-950/60 p-3 rounded border border-slate-800/80">
                    <span className="font-semibold text-indigo-300">Root-Cause Analysis: </span>
                    <span className="text-slate-300">{a.root_cause_analysis}</span>
                  </div>

                  <div className="mt-3 flex items-center justify-between text-2xs text-slate-500">
                    <span>ID: {a.anomaly_id}</span>
                    <span>{new Date(a.detected_at).toLocaleTimeString()}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center">
              <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto mb-3" />
              <h3 className="text-lg font-semibold text-white">No Acute Operational Anomalies Detected</h3>
              <p className="text-slate-400 text-sm max-w-md mx-auto mt-1">
                All ED triage queues, turnover cleaning cadences, and biomedical supplies are tracking within nominal tolerance intervals.
              </p>
            </div>
          )}
        </div>
      )}

      {/* SUB-TAB 2: COPILOT (AI Decision Support Copilot Deck) */}
      {activeSubTab === 'COPILOT' && (
        <div className="space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-indigo-400" />
              AI Clinical Operations Copilot & Priority Interventions
            </h2>
            <p className="text-slate-400 text-xs mt-1">
              Autonomous diagnostic reasoning engine mapping active operational bottlenecks into prioritized, actionable interventions with full compliance audit trails.
            </p>
          </div>

          {copilotData && copilotData.recommendations.length > 0 ? (
            <div className="space-y-4">
              {copilotData.recommendations.map((rec) => (
                <div
                  key={rec.recommendation_id}
                  className={`p-5 rounded-xl border bg-slate-900 transition ${
                    rec.urgency === 'IMMEDIATE'
                      ? 'border-indigo-500/60 bg-gradient-to-r from-slate-900 via-indigo-950/20 to-slate-900'
                      : 'border-slate-800'
                  }`}
                >
                  <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-3">
                    <div className="flex items-center gap-2">
                      <span
                        className={`px-2 py-0.5 rounded text-xs font-bold ${
                          rec.urgency === 'IMMEDIATE'
                            ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                            : rec.urgency === 'HIGH'
                            ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                            : 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                        }`}
                      >
                        {rec.urgency}
                      </span>
                      <span className="text-xs text-slate-400">
                        {rec.category} • Department: <strong className="text-slate-200">{rec.target_department}</strong>
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
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
                  </div>

                  <h3 className="text-base font-bold text-white mt-2">{rec.title}</h3>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3">
                    <div className="bg-slate-950/50 p-3 rounded-lg border border-slate-800 text-xs">
                      <div className="text-slate-400 font-medium mb-1">Clinical / Operational Rationalization:</div>
                      <p className="text-slate-300">{rec.rationalization}</p>
                    </div>

                    <div className="bg-indigo-950/20 p-3 rounded-lg border border-indigo-900/40 text-xs">
                      <div className="text-indigo-300 font-medium mb-1">Actionable Copilot Recommendation:</div>
                      <p className="text-white font-medium">{rec.recommended_action}</p>
                    </div>
                  </div>

                  <div className="mt-3 flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800/80">
                    <div>
                      <span className="font-semibold text-emerald-400">Projected Impact: </span>
                      {rec.projected_impact}
                    </div>
                  </div>

                  {/* Dispatch Controls */}
                  <div className="mt-4 pt-3 border-t border-slate-800 flex flex-col md:flex-row items-center justify-between gap-3">
                    <div className="w-full md:w-2/3">
                      <input
                        type="text"
                        placeholder="Optional authorization notes (recorded in compliance audit log)..."
                        value={actionNotes[rec.recommendation_id] || ''}
                        onChange={(e) =>
                          setActionNotes({
                            ...actionNotes,
                            [rec.recommendation_id]: e.target.value
                          })
                        }
                        className="w-full px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                      />
                    </div>

                    <div className="flex items-center gap-3 w-full md:w-auto justify-end">
                      {dispatchStatus[rec.recommendation_id] && (
                        <span className="text-xs text-indigo-400 font-medium">
                          {dispatchStatus[rec.recommendation_id]}
                        </span>
                      )}
                      <button
                        onClick={() => handleDispatchAction(rec.recommendation_id)}
                        disabled={rec.status === 'DISPATCHED'}
                        className="flex items-center gap-1.5 px-4 py-1.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-800 disabled:text-slate-600 text-white text-xs font-semibold rounded-lg shadow-md transition"
                      >
                        <Zap className="w-3.5 h-3.5" />
                        Authorize & Dispatch Action
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center">
              <CheckCircle2 className="w-12 h-12 text-indigo-400 mx-auto mb-3" />
              <h3 className="text-lg font-semibold text-white">No Active Mitigation Actions Needed</h3>
              <p className="text-slate-400 text-sm max-w-md mx-auto mt-1">
                The operations copilot has verified all clinical queues and workflows are balanced within target thresholds.
              </p>
            </div>
          )}
        </div>
      )}

      {/* SUB-TAB 3: TICKER (Live Event Stream Ticker) */}
      {activeSubTab === 'TICKER' && (
        <div className="space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
              <div>
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <Radio className="w-5 h-5 text-emerald-400 animate-pulse" />
                  Live WebSocket Operational Event Feed
                </h2>
                <p className="text-slate-400 text-xs mt-1">
                  Bi-directional streaming socket (`/ws/live-stream`). Ingests patient bed events, triage alerts, inventory adjustments, and copilot dispatches in real-time.
                </p>
              </div>

              {/* Severity Filter */}
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-400">Filter:</span>
                {['ALL', 'CRITICAL', 'WARNING', 'INFO'].map((sev) => (
                  <button
                    key={sev}
                    onClick={() => setFilterSeverity(sev)}
                    className={`px-2.5 py-1 text-xs rounded-lg font-medium transition ${
                      filterSeverity === sev
                        ? 'bg-indigo-600 text-white'
                        : 'bg-slate-800 text-slate-400 hover:text-white'
                    }`}
                  >
                    {sev}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Event Stream Log */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
            <div className="p-3 bg-slate-950/80 border-b border-slate-800 text-xs font-semibold text-slate-400 grid grid-cols-12 gap-2">
              <div className="col-span-2">TIMESTAMP</div>
              <div className="col-span-2">SEVERITY / MODULE</div>
              <div className="col-span-3">EVENT TYPE</div>
              <div className="col-span-5">MESSAGE & CONTEXT</div>
            </div>

            <div className="divide-y divide-slate-800/60 max-h-[500px] overflow-y-auto font-mono text-xs">
              {filteredEvents.length > 0 ? (
                filteredEvents.map((evt) => (
                  <div
                    key={evt.event_id}
                    className="p-3 hover:bg-slate-800/40 grid grid-cols-12 gap-2 items-center transition"
                  >
                    <div className="col-span-2 text-slate-500 flex items-center gap-1 text-2xs">
                      <Clock className="w-3 h-3 text-slate-500" />
                      {new Date(evt.timestamp).toLocaleTimeString()}
                    </div>

                    <div className="col-span-2 flex items-center gap-2">
                      <span
                        className={`px-1.5 py-0.5 rounded text-2xs font-bold ${
                          evt.severity === 'CRITICAL'
                            ? 'bg-rose-500/20 text-rose-300'
                            : evt.severity === 'WARNING'
                            ? 'bg-amber-500/20 text-amber-300'
                            : 'bg-blue-500/20 text-blue-300'
                        }`}
                      >
                        {evt.severity}
                      </span>
                      <span className="text-2xs text-slate-400 truncate">{evt.module}</span>
                    </div>

                    <div className="col-span-3 text-indigo-300 font-semibold truncate">
                      {evt.event_type}
                    </div>

                    <div className="col-span-5 text-slate-300 truncate">
                      {evt.message}
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-8 text-center text-slate-500 font-sans">
                  No events received yet. Connect to stream or trigger simulated events below.
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* SUB-TAB 4: SIMULATOR (Real-Time Chaos Simulation Rig) */}
      {activeSubTab === 'SIMULATOR' && (
        <div className="space-y-6">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5">
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Sliders className="w-5 h-5 text-amber-400" />
              Real-Time Chaos Injection & Dynamic Surge Rig
            </h2>
            <p className="text-slate-400 text-xs mt-1">
              Simulate sudden emergency department surges, sanitation bottlenecks, or supply chain stockouts to stress-test dashboard reactivity and AI Copilot mitigations.
            </p>

            {simMessage && (
              <div className="mt-3 p-3 bg-indigo-950/60 border border-indigo-800/80 rounded-lg text-xs text-indigo-200 flex items-center gap-2">
                <Send className="w-4 h-4 text-indigo-400" />
                {simMessage}
              </div>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-rose-500/10 rounded-lg text-rose-400 border border-rose-500/20">
                  <AlertTriangle className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-semibold text-white">Mass Casualty Emergency Surge</h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Injects 18 sudden trauma admissions into ED triage with ESI-1 and ESI-2 urgency.
                  </p>
                </div>
              </div>
              <button
                onClick={() =>
                  handleTriggerSim(
                    'MASS_CASUALTY_SURGE',
                    'Multiple-vehicle incident on highway: 18 acute trauma arrivals queued at ED triage.',
                    'CRITICAL',
                    { arrival_count: 18, esi_distribution: { '1': 4, '2': 8, '3': 6 } }
                  )
                }
                className="mt-4 w-full flex items-center justify-center gap-2 py-2 bg-rose-600 hover:bg-rose-500 text-white text-xs font-semibold rounded-lg shadow-md transition"
              >
                <Play className="w-3.5 h-3.5" />
                Inject Emergency Surge
              </button>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-amber-500/10 rounded-lg text-amber-400 border border-amber-500/20">
                  <Clock className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-semibold text-white">Dirty Bed Turnover Backlog</h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Simulates sanitation staff shortfall delaying bed turnaround across ICU and General Wards.
                  </p>
                </div>
              </div>
              <button
                onClick={() =>
                  handleTriggerSim(
                    'DIRTY_BED_BACKLOG',
                    '14 uncleaned beds awaiting terminal disinfection; average cleaning lag spikes to 142 mins.',
                    'WARNING',
                    { uncleaned_beds: 14, turnaround_lag_minutes: 142 }
                  )
                }
                className="mt-4 w-full flex items-center justify-center gap-2 py-2 bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold rounded-lg shadow-md transition"
              >
                <Play className="w-3.5 h-3.5" />
                Inject Turnover Lag
              </button>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-blue-500/10 rounded-lg text-blue-400 border border-blue-500/20">
                  <Activity className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-semibold text-white">Liquid Oxygen Evaporative Loss</h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Simulates rapid bulk oxygen tank draw-down reducing operational buffer to 1.8 days.
                  </p>
                </div>
              </div>
              <button
                onClick={() =>
                  handleTriggerSim(
                    'OXYGEN_SUPPLY_DEFICIT',
                    'Main cryogenic oxygen tank reserve drops to 1.8 days of supply under elevated high-flow usage.',
                    'CRITICAL',
                    { current_level_liters: 1850, days_of_supply: 1.8 }
                  )
                }
                className="mt-4 w-full flex items-center justify-center gap-2 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg shadow-md transition"
              >
                <Play className="w-3.5 h-3.5" />
                Inject Oxygen Deficit
              </button>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-purple-500/10 rounded-lg text-purple-400 border border-purple-500/20">
                  <Sparkles className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="font-semibold text-white">Pharmacy Stockout Surge</h3>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Triggers FEFO alert for zero inventory on critical broad-spectrum antibiotics (Meropenem).
                  </p>
                </div>
              </div>
              <button
                onClick={() =>
                  handleTriggerSim(
                    'MEDICATION_STOCKOUT',
                    'Zero inventory balance detected for Meropenem 1g IV; 6 scheduled patient doses unfulfilled.',
                    'CRITICAL',
                    { item_code: 'MED-MER-001', stock_balance: 0, unmet_doses: 6 }
                  )
                }
                className="mt-4 w-full flex items-center justify-center gap-2 py-2 bg-purple-600 hover:bg-purple-500 text-white text-xs font-semibold rounded-lg shadow-md transition"
              >
                <Play className="w-3.5 h-3.5" />
                Inject Stockout Alert
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
