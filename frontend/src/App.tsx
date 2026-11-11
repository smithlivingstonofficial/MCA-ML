import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { OverviewDashboard } from './pages/OverviewDashboard';
import { Cpu, HeartPulse } from 'lucide-react';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 15000,
      retry: 1,
    },
  },
});

export const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-sky-500 selection:text-slate-950">
        {/* Navigation Bar */}
        <header className="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur sticky top-0 z-40">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-500 flex items-center justify-center shadow-lg shadow-sky-500/20 text-slate-950">
                <HeartPulse className="w-5 h-5 text-white" />
              </div>
              <div>
                <span className="font-extrabold text-sm tracking-tight text-white block">
                  Antigravity Health Intelligence
                </span>
                <span className="text-[10px] text-slate-400 block tracking-wider uppercase">
                  MCA-ML • Semester III Capstone
                </span>
              </div>
            </div>

            {/* Navigation Tabs */}
            <nav className="flex items-center space-x-1 text-xs">
              <button className="px-3 py-1.5 rounded-lg font-semibold bg-sky-500/10 text-sky-400 border border-sky-500/20">
                Command Center (MVP)
              </button>
              <button
                disabled
                className="px-3 py-1.5 rounded-lg font-medium text-slate-500 cursor-not-allowed hover:text-slate-400"
                title="Phase 2 Feature"
              >
                Inventory & Staff
              </button>
              <button
                disabled
                className="px-3 py-1.5 rounded-lg font-medium text-slate-500 cursor-not-allowed hover:text-slate-400"
                title="Phase 3 Feature"
              >
                PuLP Optimization
              </button>
              <button
                disabled
                className="px-3 py-1.5 rounded-lg font-medium text-slate-500 cursor-not-allowed hover:text-slate-400"
                title="Phase 4 Feature"
              >
                Patient Continuity (SHAP)
              </button>
            </nav>
          </div>
        </header>

        {/* Main Body */}
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <OverviewDashboard />
        </main>

        {/* System Footer */}
        <footer className="border-t border-slate-900 bg-slate-950/80 py-4 text-xs text-slate-500">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <Cpu className="w-3.5 h-3.5 text-sky-400" />
              <span>Operational MVP Baseline v1.0.0 | FastAPI + SQLite + React 18 + GBDT Poisson</span>
            </div>
            <div>
              <span>Decision Support Only • Authorized Clinical Supervision Required</span>
            </div>
          </div>
        </footer>
      </div>
    </QueryClientProvider>
  );
};

export default App;
