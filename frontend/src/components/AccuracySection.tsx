import React from "react";
import type { AccuracyResponse } from "../types";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
  LineChart,
  Line
} from "recharts";
import {
  Target,
  Scale,
  Activity,
  TrendingUp,
  Percent,
  Info,
  Calendar,
  AlertCircle
} from "lucide-react";

interface AccuracySectionProps {
  accuracyData: AccuracyResponse | null;
  isLoading: boolean;
}

export const AccuracySection: React.FC<AccuracySectionProps> = ({ accuracyData, isLoading }) => {
  if (isLoading || !accuracyData) {
    return (
      <div className="card">
        <div className="card-header">
          <h2 className="card-title">Forecast Accuracy Analysis</h2>
        </div>
        <div className="loading-container">
          <div className="spinner"></div>
          <span>Computing quantitative accuracy metrics...</span>
        </div>
      </div>
    );
  }

  const { metrics, daily, hourly, distribution } = accuracyData;
  const isOverforecast = metrics.meanBias > 0;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
      {/* 1. Metric Overview Cards */}
      <div className="kpi-grid">
        {/* MAE */}
        <div className="kpi-card amber">
          <div className="kpi-header">
            <span className="kpi-title">MAE (Mean Absolute Error)</span>
            <Scale size={16} className="kpi-icon" />
          </div>
          <div className="kpi-value-row">
            <span className="kpi-value num">{metrics.mae.toLocaleString("en-GB")}</span>
            <span className="kpi-unit">MW</span>
          </div>
          <div className="kpi-footer">
            <span>Average magnitude of deviation</span>
          </div>
        </div>

        {/* RMSE */}
        <div className="kpi-card amber">
          <div className="kpi-header">
            <span className="kpi-title">RMSE (Root Mean Square Error)</span>
            <Activity size={16} className="kpi-icon" />
          </div>
          <div className="kpi-value-row">
            <span className="kpi-value num">{metrics.rmse.toLocaleString("en-GB")}</span>
            <span className="kpi-unit">MW</span>
          </div>
          <div className="kpi-footer">
            <span>Penalizes extreme forecasting shocks</span>
          </div>
        </div>

        {/* Mean Bias */}
        <div className={`kpi-card ${isOverforecast ? "rose" : "blue"}`}>
          <div className="kpi-header">
            <span className="kpi-title">Mean Error / Bias</span>
            <TrendingUp size={16} className="kpi-icon" />
          </div>
          <div className="kpi-value-row">
            <span className="kpi-value num" style={{ color: isOverforecast ? "var(--accent-rose)" : "var(--accent-blue)" }}>
              {metrics.meanBias >= 0 ? `+${metrics.meanBias}` : metrics.meanBias}
            </span>
            <span className="kpi-unit">MW</span>
          </div>
          <div className="kpi-footer">
            <span>{isOverforecast ? "Systematic Overforecast" : "Systematic Underforecast"}</span>
          </div>
        </div>

        {/* MAPE */}
        <div className="kpi-card cyan">
          <div className="kpi-header">
            <span className="kpi-title">Valid MAPE</span>
            <Percent size={16} className="kpi-icon" />
          </div>
          <div className="kpi-value-row">
            <span className="kpi-value num">
              {metrics.mape !== null ? `${metrics.mape}%` : "N/A"}
            </span>
          </div>
          <div className="kpi-footer">
            <span title="Zero/near-zero actuals excluded from denominator to avoid infinite distortion">
              {metrics.validMapeObservations} valid ({metrics.excludedZeroActualCount} zero actuals excluded)
            </span>
          </div>
        </div>
      </div>

      {/* 2. Automated Qualitative Interpretation Card */}
      <div className="interpretation-card">
        <div className="interpretation-header">
          <Info size={16} />
          <span>Automated Trading Desk Interpretation</span>
        </div>
        <p className="interpretation-body">{metrics.interpretation}</p>
      </div>

      {/* 3. Error Distribution & Hourly Diurnal Profile Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(450px, 1fr))", gap: "20px" }}>
        {/* Error Distribution Histogram */}
        <div className="card">
          <div className="card-header">
            <div className="card-title-group">
              <h3 className="card-title">Forecast Error Distribution (MW)</h3>
              <p className="card-subtitle">
                Frequency of error buckets: Negative = Underforecast, Positive = Overforecast
              </p>
            </div>
          </div>
          <div style={{ height: 260 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={distribution} margin={{ top: 10, right: 10, left: 0, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
                <XAxis dataKey="rangeLabel" stroke="#64748B" fontSize={10} interval={0} angle={-15} textAnchor="end" />
                <YAxis stroke="#64748B" fontSize={11} unit="%" />
                <Tooltip
                  formatter={(val: any, _name: any, item: any) => [
                    `${val}% (${item.payload.count} intervals)`,
                    "Frequency",
                  ]}
                  contentStyle={{ backgroundColor: "#0E1626", borderColor: "#2A3F66", fontSize: "12px" }}
                />
                <Bar dataKey="percentage" radius={[4, 4, 0, 0]}>
                  {distribution.map((entry, index) => {
                    const isPos = entry.minVal >= 250;
                    const isNeg = entry.maxVal <= -250;
                    const color = isPos ? "var(--accent-rose)" : isNeg ? "var(--accent-cyan)" : "var(--accent-emerald)";
                    return <Cell key={`cell-${index}`} fill={color} />;
                  })}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Diurnal Hourly Bias Profile */}
        <div className="card">
          <div className="card-header">
            <div className="card-title-group">
              <h3 className="card-title">Diurnal Hourly Bias Profile (UK Local Time)</h3>
              <p className="card-subtitle">
                Mean forecast error by hour of day (00:00 to 23:00) showing intraday ramp bias
              </p>
            </div>
          </div>
          <div style={{ height: 260 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={hourly} margin={{ top: 10, right: 10, left: 10, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
                <XAxis dataKey="hour" stroke="#64748B" fontSize={11} tickFormatter={(h) => `${h}:00`} />
                <YAxis stroke="#64748B" fontSize={11} unit=" MW" />
                <Tooltip
                  formatter={(val: any, name: any) => [`${val} MW`, name]}
                  labelFormatter={(h) => `Hour ${h}:00 UK Time`}
                  contentStyle={{ backgroundColor: "#0E1626", borderColor: "#2A3F66", fontSize: "12px" }}
                />
                <Line
                  type="monotone"
                  dataKey="meanBias"
                  name="Mean Bias (MW)"
                  stroke="#F59E0B"
                  strokeWidth={2}
                  dot={{ r: 3, fill: "#F59E0B" }}
                />
                <Line
                  type="monotone"
                  dataKey="mae"
                  name="Hourly MAE (MW)"
                  stroke="#06B6D4"
                  strokeWidth={1.5}
                  strokeDasharray="4 4"
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* 4. Daily Accuracy Breakdown Table */}
      <div className="card">
        <div className="card-header">
          <div className="card-title-group">
            <h3 className="card-title">Daily Forecast Accuracy Performance Breakdown</h3>
            <p className="card-subtitle">
              Daily error metrics, forecast energy vs delivered outturn, and energy variance
            </p>
          </div>
        </div>

        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Delivery Date</th>
                <th>MAE (MW)</th>
                <th>RMSE (MW)</th>
                <th>Mean Bias (MW)</th>
                <th>Forecast Energy (MWh)</th>
                <th>Actual Energy (MWh)</th>
                <th>Variance (MWh)</th>
                <th>Max Overforecast</th>
                <th>Max Underforecast</th>
                <th>Intervals</th>
              </tr>
            </thead>
            <tbody>
              {daily.map((d) => (
                <tr key={d.date}>
                  <td><strong>{d.date}</strong></td>
                  <td className="num">{d.mae.toLocaleString("en-GB")}</td>
                  <td className="num">{d.rmse.toLocaleString("en-GB")}</td>
                  <td className="num" style={{ color: d.meanBias > 0 ? "var(--accent-rose)" : "var(--accent-cyan)" }}>
                    {d.meanBias > 0 ? `+${d.meanBias}` : d.meanBias}
                  </td>
                  <td className="num">{d.forecastEnergyMwh.toLocaleString("en-GB")}</td>
                  <td className="num">{d.actualEnergyMwh.toLocaleString("en-GB")}</td>
                  <td className="num" style={{ color: d.energyVarianceMwh > 0 ? "var(--accent-rose)" : "var(--accent-cyan)" }}>
                    {d.energyVarianceMwh > 0 ? `+${d.energyVarianceMwh.toLocaleString("en-GB")}` : d.energyVarianceMwh.toLocaleString("en-GB")}
                  </td>
                  <td className="num" style={{ color: "var(--accent-rose)" }}>+{d.maxOverforecastMw.toLocaleString("en-GB")} MW</td>
                  <td className="num" style={{ color: "var(--accent-cyan)" }}>-{d.maxUnderforecastMw.toLocaleString("en-GB")} MW</td>
                  <td>{d.matchedIntervals}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
