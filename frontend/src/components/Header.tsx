import React from "react";
import { RefreshCw, Wind, ShieldCheck, Database, Clock } from "lucide-react";
import type { ExecutiveSummaryKpis } from "../types";

interface HeaderProps {
  kpis: ExecutiveSummaryKpis | null;
  isLoading: boolean;
  onRefresh: () => void;
}

export const Header: React.FC<HeaderProps> = ({ kpis, isLoading, onRefresh }) => {
  const isDemo = kpis?.isDemoData ?? false;
  const freshness = kpis?.dataFreshness ?? "LIVE_ELEXON";
  const lastRefresh = kpis?.lastRefreshUtc
    ? new Date(kpis.lastRefreshUtc).toLocaleTimeString("en-GB", { timeZone: "UTC", hour: "2-digit", minute: "2-digit", second: "2-digit" }) + " UTC"
    : "--:--:--";

  return (
    <header className="top-header">
      <div className="header-left">
        <div className="header-title-row">
          <h1 className="header-title">UK Wind Power Forecast & Day-Ahead Procurement Analytics</h1>
          {isDemo ? (
            <span className="status-pill demo" title="Synthetic fallback demo data actively illustrating UI">
              <span className="status-dot"></span>
              DEMO MODE
            </span>
          ) : (
            <span className="status-pill live" title="Direct live stream from Elexon BMRS API">
              <span className="status-dot pulse"></span>
              ELEXON LIVE
            </span>
          )}
        </div>
        <p className="header-subtitle">
          National Grid ESO Day-Ahead Wind Forecast (WINDFOR) vs Settlement Outturn (FUELHH) • Great Britain Market
        </p>
      </div>

      <div className="header-right">
        <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: "2px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "11px", color: "var(--text-muted)" }}>
            <Clock size={12} />
            <span>Updated:</span>
            <strong style={{ color: "var(--text-secondary)", fontFamily: "var(--font-mono)" }}>{lastRefresh}</strong>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "11px", color: "var(--text-muted)" }}>
            <Database size={12} />
            <span>Cutoff:</span>
            <span style={{ color: "var(--accent-cyan)", fontFamily: "var(--font-mono)" }}>
              {kpis?.selectedDecisionCutoff || "11:00 Europe/London (D-1)"}
            </span>
          </div>
        </div>

        <button
          className="btn-secondary"
          onClick={onRefresh}
          disabled={isLoading}
          title="Force refresh data from Elexon API"
        >
          <RefreshCw size={14} className={isLoading ? "spinner" : ""} />
          <span>Refresh</span>
        </button>
      </div>
    </header>
  );
};
