import React from "react";
import {
  Wind,
  Zap,
  CheckCircle2,
  AlertTriangle,
  Scale,
  TrendingUp,
  Activity,
  BarChart2
} from "lucide-react";
import type { ExecutiveSummaryKpis } from "../types";

interface KpiGridProps {
  kpis: ExecutiveSummaryKpis | null;
  isLoading: boolean;
}

export const KpiGrid: React.FC<KpiGridProps> = ({ kpis, isLoading }) => {
  if (isLoading || !kpis) {
    return (
      <div className="kpi-grid">
        {[...Array(8)].map((_, i) => (
          <div key={i} className="kpi-card" style={{ opacity: 0.6 }}>
            <div className="kpi-header">
              <span className="kpi-title">Loading Metric...</span>
            </div>
            <div className="kpi-value-row">
              <span className="kpi-value">---</span>
            </div>
          </div>
        ))}
      </div>
    );
  }

  const isOverforecast = kpis.meanBiasMw > 0;

  return (
    <div className="kpi-grid">
      {/* 1. Latest Eligible Forecast */}
      <div className="kpi-card cyan">
        <div className="kpi-header">
          <span className="kpi-title">Latest Eligible Forecast</span>
          <Wind size={16} className="kpi-icon" />
        </div>
        <div className="kpi-value-row">
          <span className="kpi-value num">
            {kpis.latestEligibleForecastMw !== null
              ? kpis.latestEligibleForecastMw.toLocaleString("en-GB", { maximumFractionDigits: 0 })
              : "N/A"}
          </span>
          <span className="kpi-unit">MW</span>
        </div>
        <div className="kpi-footer">
          <span>Snapshot prior to gate closure</span>
        </div>
      </div>

      {/* 2. Total Forecast Energy */}
      <div className="kpi-card cyan">
        <div className="kpi-header">
          <span className="kpi-title">Forecast Energy (Period)</span>
          <Zap size={16} className="kpi-icon" />
        </div>
        <div className="kpi-value-row">
          <span className="kpi-value num">
            {kpis.totalForecastEnergyGwh.toLocaleString("en-GB", { maximumFractionDigits: 1 })}
          </span>
          <span className="kpi-unit">GWh</span>
        </div>
        <div className="kpi-footer">
          <span>Day-ahead planned volume</span>
        </div>
      </div>

      {/* 3. Total Actual Energy */}
      <div className="kpi-card emerald">
        <div className="kpi-header">
          <span className="kpi-title">Actual Outturn Energy</span>
          <CheckCircle2 size={16} className="kpi-icon" />
        </div>
        <div className="kpi-value-row">
          <span className="kpi-value num">
            {kpis.totalActualEnergyGwh.toLocaleString("en-GB", { maximumFractionDigits: 1 })}
          </span>
          <span className="kpi-unit">GWh</span>
        </div>
        <div className="kpi-footer">
          <span>Delivered settlement outturn (FUELHH)</span>
        </div>
      </div>

      {/* 4. MAE */}
      <div className="kpi-card amber">
        <div className="kpi-header">
          <span className="kpi-title">Forecast MAE</span>
          <Scale size={16} className="kpi-icon" />
        </div>
        <div className="kpi-value-row">
          <span className="kpi-value num">
            {kpis.maeMw.toLocaleString("en-GB", { maximumFractionDigits: 1 })}
          </span>
          <span className="kpi-unit">MW</span>
        </div>
        <div className="kpi-footer">
          <span>Mean Absolute Error magnitude</span>
        </div>
      </div>

      {/* 5. RMSE */}
      <div className="kpi-card amber">
        <div className="kpi-header">
          <span className="kpi-title">Forecast RMSE</span>
          <Activity size={16} className="kpi-icon" />
        </div>
        <div className="kpi-value-row">
          <span className="kpi-value num">
            {kpis.rmseMw.toLocaleString("en-GB", { maximumFractionDigits: 1 })}
          </span>
          <span className="kpi-unit">MW</span>
        </div>
        <div className="kpi-footer">
          <span>Root Mean Squared Error (penalizes spikes)</span>
        </div>
      </div>

      {/* 6. Mean Forecast Bias */}
      <div className={`kpi-card ${isOverforecast ? "rose" : "blue"}`}>
        <div className="kpi-header">
          <span className="kpi-title">Mean Forecast Bias</span>
          <TrendingUp size={16} className="kpi-icon" />
        </div>
        <div className="kpi-value-row">
          <span className="kpi-value num" style={{ color: isOverforecast ? "var(--accent-rose)" : "var(--accent-blue)" }}>
            {kpis.meanBiasMw >= 0 ? `+${kpis.meanBiasMw}` : kpis.meanBiasMw}
          </span>
          <span className="kpi-unit">MW</span>
        </div>
        <div className="kpi-footer">
          <span style={{ fontWeight: 600, color: isOverforecast ? "var(--accent-rose)" : "var(--accent-blue)" }}>
            {isOverforecast ? "OVERFORECASTING (Deficit Risk)" : "UNDERFORECASTING (Surplus)"}
          </span>
        </div>
      </div>

      {/* 7. Potential Shortfall Volume */}
      <div className="kpi-card rose">
        <div className="kpi-header">
          <span className="kpi-title">Potential Wind Shortfall</span>
          <AlertTriangle size={16} className="kpi-icon" />
        </div>
        <div className="kpi-value-row">
          <span className="kpi-value num" style={{ color: "var(--accent-rose)" }}>
            {kpis.totalShortfallEnergyGwh.toLocaleString("en-GB", { maximumFractionDigits: 1 })}
          </span>
          <span className="kpi-unit">GWh</span>
        </div>
        <div className="kpi-footer">
          <span>Peak deficit: <strong>{kpis.maxShortfallMw.toLocaleString("en-GB")} MW</strong></span>
        </div>
      </div>

      {/* 8. Matched Observations */}
      <div className="kpi-card blue">
        <div className="kpi-header">
          <span className="kpi-title">Matched Observations</span>
          <BarChart2 size={16} className="kpi-icon" />
        </div>
        <div className="kpi-value-row">
          <span className="kpi-value num">
            {kpis.totalMatchedObservations.toLocaleString("en-GB")}
          </span>
          <span className="kpi-unit">intervals</span>
        </div>
        <div className="kpi-footer">
          <span>Overforecast in <strong>{kpis.overforecastRatePct}%</strong> of hours</span>
        </div>
      </div>
    </div>
  );
};
