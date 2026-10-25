import React from "react";
import type { ProcurementAnalysisResponse } from "../types";
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
import {
  AlertTriangle,
  ShieldAlert,
  TrendingDown,
  Info,
  Clock,
  ArrowDownRight
} from "lucide-react";

interface ProcurementInsightsPanelProps {
  procurementData: ProcurementAnalysisResponse | null;
  isLoading: boolean;
}

export const ProcurementInsightsPanel: React.FC<ProcurementInsightsPanelProps> = ({
  procurementData,
  isLoading,
}) => {
  if (isLoading || !procurementData) {
    return (
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Potential Additional Procurement</h2>
        </div>
        <div className="loading-container">
          <div className="spinner"></div>
          <span>Calculating wind generation shortfall and downside scenarios...</span>
        </div>
      </div>
    );
  }

  // Find top 5 shortfall intervals
  const topShortfalls = [...procurementData.points]
    .filter((p) => p.shortfallMw > 0)
    .sort((a, b) => b.shortfallMw - a.shortfallMw)
    .slice(0, 5);

  const chartData = procurementData.points.map((p) => ({
    ...p,
    timeLabel: p.startTimeLocal ? p.startTimeLocal.replace(" GMT", "").replace(" BST", "") : p.startTime,
  }));

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      {/* 1. Mandatory Operational Notice & Legal Disclaimer */}
      <div className="disclaimer-banner">
        <ShieldAlert size={24} style={{ color: "var(--accent-amber)", flexShrink: 0, marginTop: "2px" }} />
        <div>
          <strong>Operational Procurement Notice & Dataset Boundary:</strong>
          <p style={{ marginTop: "4px" }}>
            {procurementData.operationalDisclaimer}
          </p>
        </div>
      </div>

      {/* 2. Top Summary KPI Cards */}
      <div className="kpi-grid">
        <div className="kpi-card rose">
          <div className="kpi-header">
            <span className="kpi-title">Total Shortfall Volume</span>
            <AlertTriangle size={16} className="kpi-icon" />
          </div>
          <div className="kpi-value-row">
            <span className="kpi-value num">
              {procurementData.totalShortfallEnergyMwh.toLocaleString("en-GB", { maximumFractionDigits: 1 })}
            </span>
            <span className="kpi-unit">MWh</span>
          </div>
          <div className="kpi-footer">
            <span>Cumulative wind deficit across period</span>
          </div>
        </div>

        <div className="kpi-card rose">
          <div className="kpi-header">
            <span className="kpi-title">Peak Single-Interval Shortfall</span>
            <ArrowDownRight size={16} className="kpi-icon" />
          </div>
          <div className="kpi-value-row">
            <span className="kpi-value num">
              {procurementData.maxShortfallMw.toLocaleString("en-GB")}
            </span>
            <span className="kpi-unit">MW</span>
          </div>
          <div className="kpi-footer">
            <span>Maximum single hourly shortfall</span>
          </div>
        </div>

        <div className="kpi-card amber">
          <div className="kpi-header">
            <span className="kpi-title">Mean Shortfall (When in Deficit)</span>
            <TrendingDown size={16} className="kpi-icon" />
          </div>
          <div className="kpi-value-row">
            <span className="kpi-value num">
              {procurementData.meanShortfallWhenDeficitMw.toLocaleString("en-GB", { maximumFractionDigits: 1 })}
            </span>
            <span className="kpi-unit">MW</span>
          </div>
          <div className="kpi-footer">
            <span>Average deficit during shortfall hours</span>
          </div>
        </div>

        <div className="kpi-card blue">
          <div className="kpi-header">
            <span className="kpi-title">Shortfall Frequency</span>
            <Clock size={16} className="kpi-icon" />
          </div>
          <div className="kpi-value-row">
            <span className="kpi-value num">{procurementData.shortfallPercentage}%</span>
            <span className="kpi-unit">of intervals</span>
          </div>
          <div className="kpi-footer">
            <span>{procurementData.shortfallIntervalsCount} deficit intervals recorded</span>
          </div>
        </div>
      </div>

      {/* 3. Downside P10 Scenario Chart */}
      <div className="card">
        <div className="card-header">
          <div className="card-title-group">
            <h3 className="card-title">Wind Procurement Risk Profile & Downside Scenario</h3>
            <p className="card-subtitle">
              Forecast vs Conservative P10 Downside Scenario vs Realized Generation Outturn (MW)
            </p>
          </div>
        </div>

        <div style={{ height: 320 }}>
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={chartData} margin={{ top: 10, right: 15, left: 10, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
              <XAxis dataKey="timeLabel" stroke="#64748B" fontSize={11} minTickGap={45} />
              <YAxis stroke="#64748B" fontSize={11} unit=" MW" tickFormatter={(v) => `${(v / 1000).toFixed(0)}k`} />
              <Tooltip
                contentStyle={{ backgroundColor: "#0E1626", borderColor: "#2A3F66", fontSize: "12px" }}
                formatter={(val: any, name: any) => [`${Number(val).toLocaleString("en-GB")} MW`, name]}
              />
              <Legend verticalAlign="top" height={36} />

              <Line
                type="monotone"
                dataKey="generationForecast"
                name="Day-Ahead Forecast (MW)"
                stroke="#06B6D4"
                strokeWidth={2}
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="downsideScenarioMw"
                name="Conservative P10 Downside (MW)"
                stroke="#F59E0B"
                strokeWidth={1.8}
                strokeDasharray="4 4"
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="generationActual"
                name="Realized Outturn (MW)"
                stroke="#10B981"
                strokeWidth={1.8}
                dot={false}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        <div style={{ marginTop: "14px", padding: "12px", background: "rgba(255,255,255,0.02)", borderRadius: "var(--radius-md)", fontSize: "12px", color: "var(--text-secondary)" }}>
          <strong>Downside Scenario Methodology:</strong> {procurementData.downsideMethodology}
        </div>
      </div>

      {/* 4. Top Shortfall Intervals Table */}
      <div className="card">
        <div className="card-header">
          <div className="card-title-group">
            <h3 className="card-title">Top 5 Extreme Wind Shortfall Events</h3>
            <p className="card-subtitle">
              Largest individual negative generation shocks requiring intraday market replacement
            </p>
          </div>
        </div>

        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Delivery Interval (UK Local)</th>
                <th>Day-Ahead Forecast</th>
                <th>Actual Outturn</th>
                <th>Shortfall Deficit</th>
                <th>Forecast Publication Snapshot</th>
                <th>Decision Cutoff</th>
              </tr>
            </thead>
            <tbody>
              {topShortfalls.map((p, idx) => (
                <tr key={idx}>
                  <td><strong>{p.startTimeLocal}</strong></td>
                  <td className="num">{p.generationForecast.toLocaleString("en-GB")} MW</td>
                  <td className="num">{p.generationActual?.toLocaleString("en-GB") ?? "N/A"} MW</td>
                  <td className="num" style={{ color: "var(--accent-rose)", fontWeight: 600 }}>
                    +{p.shortfallMw.toLocaleString("en-GB")} MW
                  </td>
                  <td>{p.publishTimeLocal}</td>
                  <td>{p.decisionCutoffLocal}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
