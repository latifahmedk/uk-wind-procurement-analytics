import React, { useState } from "react";
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from "recharts";
import type { MatchedTimeseriesPoint } from "../types";
import { Layers, Eye, EyeOff } from "lucide-react";

interface ForecastActualChartProps {
  timeseriesData: MatchedTimeseriesPoint[];
  isLoading: boolean;
}

export const ForecastActualChart: React.FC<ForecastActualChartProps> = ({
  timeseriesData,
  isLoading,
}) => {
  const [showForecast, setShowForecast] = useState(true);
  const [showActual, setShowActual] = useState(true);
  const [showShortfall, setShowShortfall] = useState(true);

  if (isLoading) {
    return (
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Forecast vs Actual Wind Generation</h2>
        </div>
        <div className="loading-container">
          <div className="spinner"></div>
          <span>Loading time series data...</span>
        </div>
      </div>
    );
  }

  if (!timeseriesData || timeseriesData.length === 0) {
    return (
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Forecast vs Actual Wind Generation</h2>
        </div>
        <div style={{ textAlign: "center", padding: "40px", color: "var(--text-muted)" }}>
          No matched time series observations available for the active filters.
        </div>
      </div>
    );
  }

  // Format data for Recharts
  const chartData = timeseriesData.map((d) => ({
    ...d,
    timeLabel: d.startTimeLocal ? d.startTimeLocal.replace(" GMT", "").replace(" BST", "") : d.startTime,
  }));

  const CustomTooltipContent = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data: MatchedTimeseriesPoint = payload[0].payload;
      const error = data.forecastError;
      const isOver = error > 0;

      return (
        <div className="custom-tooltip">
          <div className="tooltip-time">{data.startTimeLocal || data.startTime}</div>
          <div className="tooltip-row">
            <span>
              <span className="tooltip-badge" style={{ backgroundColor: "var(--accent-cyan)" }}></span>
              Day-Ahead Forecast:
            </span>
            <strong className="num">{data.generationForecast?.toLocaleString("en-GB")} MW</strong>
          </div>
          <div className="tooltip-row">
            <span>
              <span className="tooltip-badge" style={{ backgroundColor: "var(--accent-emerald)" }}></span>
              Actual Outturn:
            </span>
            <strong className="num">{data.generationActual?.toLocaleString("en-GB")} MW</strong>
          </div>
          <div className="tooltip-row" style={{ borderTop: "1px dashed var(--border-subtle)", paddingTop: "4px", marginTop: "4px" }}>
            <span>Forecast Error:</span>
            <strong className="num" style={{ color: isOver ? "var(--accent-rose)" : "var(--accent-cyan)" }}>
              {error > 0 ? `+${error.toLocaleString("en-GB")}` : error.toLocaleString("en-GB")} MW
            </strong>
          </div>
          {data.shortfallMw > 0 && (
            <div className="tooltip-row">
              <span style={{ color: "var(--accent-rose)" }}>Wind Shortfall:</span>
              <strong className="num" style={{ color: "var(--accent-rose)" }}>
                {data.shortfallMw.toLocaleString("en-GB")} MW
              </strong>
            </div>
          )}
          <div style={{ marginTop: "6px", fontSize: "10px", color: "var(--text-muted)", borderTop: "1px solid var(--border-subtle)", paddingTop: "4px" }}>
            Snapshot Pub: <span style={{ color: "var(--text-secondary)" }}>{data.publishTimeLocal || data.publishTime}</span>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title-group">
          <h2 className="card-title">
            <span>National Wind Generation: Day-Ahead Forecast vs Delivered Outturn</span>
          </h2>
          <p className="card-subtitle">
            Hourly average generation in Megawatts (MW) • Elexon WINDFOR snapshot selected prior to gate closure vs FUELHH
          </p>
        </div>

        {/* Visibility Toggles */}
        <div style={{ display: "flex", gap: "10px" }}>
          <button
            className={`btn-secondary ${showForecast ? "active" : ""}`}
            style={{ fontSize: "11px", padding: "4px 8px" }}
            onClick={() => setShowForecast(!showForecast)}
          >
            <span style={{ width: 8, height: 8, borderRadius: "50%", backgroundColor: "var(--accent-cyan)" }}></span>
            <span>Forecast</span>
          </button>
          <button
            className={`btn-secondary ${showActual ? "active" : ""}`}
            style={{ fontSize: "11px", padding: "4px 8px" }}
            onClick={() => setShowActual(!showActual)}
          >
            <span style={{ width: 8, height: 8, borderRadius: "50%", backgroundColor: "var(--accent-emerald)" }}></span>
            <span>Actual</span>
          </button>
          <button
            className={`btn-secondary ${showShortfall ? "active" : ""}`}
            style={{ fontSize: "11px", padding: "4px 8px" }}
            onClick={() => setShowShortfall(!showShortfall)}
          >
            <span style={{ width: 8, height: 8, borderRadius: "50%", backgroundColor: "var(--accent-rose)" }}></span>
            <span>Shortfall Area</span>
          </button>
        </div>
      </div>

      <div className="chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chartData} margin={{ top: 10, right: 20, left: 10, bottom: 25 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
            <XAxis
              dataKey="timeLabel"
              stroke="#64748B"
              fontSize={11}
              tickLine={false}
              minTickGap={45}
            />
            <YAxis
              stroke="#64748B"
              fontSize={11}
              tickLine={false}
              unit=" MW"
              tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`}
            />
            <Tooltip content={<CustomTooltipContent />} />
            <Legend verticalAlign="top" height={36} />

            {/* Shortfall shading area */}
            {showShortfall && (
              <Area
                type="monotone"
                dataKey="shortfallMw"
                name="Wind Shortfall Deficit (MW)"
                fill="rgba(244, 63, 94, 0.2)"
                stroke="rgba(244, 63, 94, 0.4)"
                strokeWidth={1}
              />
            )}

            {/* Selected Forecast Curve */}
            {showForecast && (
              <Line
                type="monotone"
                dataKey="generationForecast"
                name="Eligible Day-Ahead Forecast (MW)"
                stroke="#06B6D4"
                strokeWidth={2.2}
                dot={false}
                activeDot={{ r: 5, fill: "#06B6D4" }}
              />
            )}

            {/* Actual Outturn Curve */}
            {showActual && (
              <Line
                type="monotone"
                dataKey="generationActual"
                name="Actual Generation Outturn (MW)"
                stroke="#10B981"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 5, fill: "#10B981" }}
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
