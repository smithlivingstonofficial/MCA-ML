import React, { useState } from 'react';
import { Calendar, TrendingUp, AlertCircle, Info } from 'lucide-react';
import { ArrivalForecastResponse, HourlyForecastPoint } from '../../types';

interface ForecastChartProps {
  forecastData?: ArrivalForecastResponse;
  isLoading: boolean;
  onHorizonChange: (horizon: number) => void;
  currentHorizon: number;
}

export const ForecastChart: React.FC<ForecastChartProps> = ({
  forecastData,
  isLoading,
  onHorizonChange,
  currentHorizon,
}) => {
  const [hoveredPoint, setHoveredPoint] = useState<HourlyForecastPoint | null>(null);

  if (isLoading || !forecastData) {
    return (
      <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl animate-pulse h-80">
        <div className="h-6 w-48 bg-slate-800 rounded mb-4"></div>
        <div className="h-60 bg-slate-800/40 rounded"></div>
      </div>
    );
  }

  const points = forecastData.forecasts;
  const maxVal = Math.max(...points.map((p) => p.upper_bound_80), 16);
  const minVal = 0;

  // SVG dimensions
  const svgWidth = 800;
  const svgHeight = 220;
  const padding = { top: 20, right: 30, bottom: 30, left: 40 };
  const graphWidth = svgWidth - padding.left - padding.right;
  const graphHeight = svgHeight - padding.top - padding.bottom;

  const getX = (index: number) => padding.left + (index / (points.length - 1)) * graphWidth;
  const getY = (val: number) => padding.top + graphHeight - ((val - minVal) / (maxVal - minVal)) * graphHeight;

  // Build line path for predicted values
  const linePath = points
    .map((p, idx) => `${idx === 0 ? 'M' : 'L'} ${getX(idx)} ${getY(p.predicted_arrivals)}`)
    .join(' ');

  // Build upper bound and reverse lower bound for 80% confidence envelope
  const upperPath = points.map((p, idx) => `${idx === 0 ? 'M' : 'L'} ${getX(idx)} ${getY(p.upper_bound_80)}`).join(' ');
  const lowerPathReverse = [...points]
    .reverse()
    .map((p, idx) => `L ${getX(points.length - 1 - idx)} ${getY(p.lower_bound_80)}`)
    .join(' ');
  const areaPath = `${upperPath} ${lowerPathReverse} Z`;

  const thresholdY = getY(12.0);

  return (
    <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl relative">
      {/* Header with Title and Horizon Buttons */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-4">
        <div>
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-sky-400" />
            <h2 className="text-base font-bold text-white">Module 1: Emergency Department Arrival Forecast</h2>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Hourly demand projections with 80% prediction interval bands (Poisson GBDT)
          </p>
        </div>

        {/* Horizon Toggle */}
        <div className="flex items-center gap-1.5 bg-slate-950 p-1 rounded-xl border border-slate-800">
          {[24, 48, 72].map((h) => (
            <button
              key={h}
              onClick={() => onHorizonChange(h)}
              className={`px-3 py-1 text-xs font-semibold rounded-lg transition-all ${
                currentHorizon === h
                  ? 'bg-sky-500 text-slate-950 shadow-sm'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              {h}h Ahead
            </button>
          ))}
        </div>
      </div>

      {/* SVG Chart */}
      <div className="relative overflow-x-auto">
        <svg
          viewBox={`0 0 ${svgWidth} ${svgHeight}`}
          className="w-full h-auto max-h-64"
        >
          {/* Grid lines */}
          {[0, 4, 8, 12, 16].map((tick) => (
            <g key={tick}>
              <line
                x1={padding.left}
                y1={getY(tick)}
                x2={svgWidth - padding.right}
                y2={getY(tick)}
                stroke="#1e293b"
                strokeDasharray="4 4"
              />
              <text
                x={padding.left - 8}
                y={getY(tick) + 4}
                fill="#64748b"
                fontSize="10"
                textAnchor="end"
              >
                {tick}
              </text>
            </g>
          ))}

          {/* Overcrowding Alert Threshold (12/hr) */}
          <line
            x1={padding.left}
            y1={thresholdY}
            x2={svgWidth - padding.right}
            y2={thresholdY}
            stroke="#f43f5e"
            strokeWidth="1.5"
            strokeDasharray="6 3"
          />
          <text
            x={svgWidth - padding.right - 5}
            y={thresholdY - 6}
            fill="#f43f5e"
            fontSize="10"
            textAnchor="end"
            fontWeight="bold"
          >
            Capacity Threshold (12/hr)
          </text>

          {/* 80% Prediction Interval Shading */}
          <path d={areaPath} fill="#0284c7" fillOpacity="0.12" />

          {/* Forecast Trend Line */}
          <path
            d={linePath}
            fill="none"
            stroke="#38bdf8"
            strokeWidth="2.5"
            strokeLinecap="round"
          />

          {/* Data Points */}
          {points.map((p, idx) => {
            const x = getX(idx);
            const y = getY(p.predicted_arrivals);
            const isOvercrowded = p.overcrowding_risk;
            return (
              <circle
                key={idx}
                cx={x}
                cy={y}
                r={isOvercrowded ? 4.5 : 3}
                fill={isOvercrowded ? '#f43f5e' : '#38bdf8'}
                stroke="#0f172a"
                strokeWidth="2"
                className="cursor-pointer transition-transform hover:scale-150"
                onMouseEnter={() => setHoveredPoint(p)}
                onMouseLeave={() => setHoveredPoint(null)}
              />
            );
          })}
        </svg>

        {/* Hover Tooltip Overlay */}
        {hoveredPoint && (
          <div className="absolute top-2 right-4 bg-slate-950/95 border border-slate-700/80 p-3 rounded-xl shadow-2xl text-xs space-y-1 pointer-events-none backdrop-blur">
            <div className="font-semibold text-white flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5 text-sky-400" />
              {new Date(hoveredPoint.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', month: 'short', day: 'numeric' })}
            </div>
            <div className="text-sky-400 font-bold text-sm">
              Predicted: {hoveredPoint.predicted_arrivals} arrivals/hr
            </div>
            <div className="text-slate-400">
              80% Interval: [{hoveredPoint.lower_bound_80} - {hoveredPoint.upper_bound_80}]
            </div>
            {hoveredPoint.overcrowding_risk && (
              <div className="text-rose-400 font-bold flex items-center gap-1 mt-1">
                <AlertCircle className="w-3.5 h-3.5" /> High Overcrowding Risk
              </div>
            )}
          </div>
        )}
      </div>

      {/* Legend & Telemetry Context Footer */}
      <div className="mt-4 pt-3 border-t border-slate-800/80 flex flex-wrap items-center justify-between text-xs text-slate-400 gap-2">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-0.5 bg-sky-400"></span>
            <span>Expected Arrivals</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 bg-sky-500/20 border border-sky-400/40 rounded-sm"></span>
            <span>80% Prediction Band</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>
            <span>Surge Alert Point</span>
          </div>
        </div>

        <div className="flex items-center gap-2 text-slate-500">
          <Info className="w-3.5 h-3.5" />
          <span>Model: HistGBDT (Poisson) | Out-of-sample WAPE: 30.5% (+25.5% over Naive)</span>
        </div>
      </div>
    </div>
  );
};

