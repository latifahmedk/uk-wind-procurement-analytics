import React from "react";
import { Calendar, Clock, SlidersHorizontal, HelpCircle } from "lucide-react";
import type { QueryParams } from "../services/api";

interface ControlsBarProps {
  filters: QueryParams;
  onFilterChange: (newFilters: Partial<QueryParams>) => void;
  availableCutoffs?: { time: string; label: string; description: string }[];
}

export const ControlsBar: React.FC<ControlsBarProps> = ({
  filters,
  onFilterChange,
  availableCutoffs = [],
}) => {
  const presets = [
    { label: "Full Jan 2026", start: "2026-01-01", end: "2026-01-31" },
    { label: "Week 1 (Jan 1-7)", start: "2026-01-01", end: "2026-01-07" },
    { label: "Week 2 (Jan 8-14)", start: "2026-01-08", end: "2026-01-14" },
    { label: "Week 3 (Jan 15-21)", start: "2026-01-15", end: "2026-01-21" },
    { label: "Week 4 (Jan 22-28)", start: "2026-01-22", end: "2026-01-28" },
    { label: "Jan 29 - Feb 1", start: "2026-01-29", end: "2026-02-01" },
  ];

  return (
    <div className="controls-bar">
      {/* Date Range & Presets */}
      <div className="controls-group">
        <span className="control-label" style={{ display: "flex", alignItems: "center", gap: "4px" }}>
          <Calendar size={14} /> Date Range:
        </span>
        <input
          type="date"
          className="date-input"
          value={filters.startDate}
          min="2024-01-01"
          max="2026-02-05"
          onChange={(e) => onFilterChange({ startDate: e.target.value })}
        />
        <span style={{ color: "var(--text-muted)" }}>to</span>
        <input
          type="date"
          className="date-input"
          value={filters.endDate}
          min="2024-01-01"
          max="2026-02-05"
          onChange={(e) => onFilterChange({ endDate: e.target.value })}
        />

        {/* Quick Presets */}
        <div style={{ display: "flex", gap: "4px", flexWrap: "wrap" }}>
          {presets.map((p) => {
            const isActive = filters.startDate === p.start && filters.endDate === p.end;
            return (
              <button
                key={p.label}
                className="btn-secondary"
                style={{
                  padding: "4px 8px",
                  fontSize: "11px",
                  backgroundColor: isActive ? "var(--bg-surface-hover)" : undefined,
                  borderColor: isActive ? "var(--accent-cyan)" : undefined,
                  color: isActive ? "#FFFFFF" : undefined,
                }}
                onClick={() => onFilterChange({ startDate: p.start, endDate: p.end })}
              >
                {p.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Cohort & Gate Closure Cutoff */}
      <div className="controls-group">
        <span className="control-label">Filter Mode:</span>
        <select
          className="select-input"
          value={filters.filterBy}
          onChange={(e) => onFilterChange({ filterBy: e.target.value as "delivery_date" | "decision_date" })}
          title="Delivery Date filters by power delivery window; Decision Date cohorts decisions made in Jan 2026 (delivering up to Feb 1)"
        >
          <option value="delivery_date">Delivery Date (Power Delivered)</option>
          <option value="decision_date">Decision Date (Procurement Cohort D-1)</option>
        </select>

        <span className="control-label" style={{ display: "flex", alignItems: "center", gap: "4px" }}>
          <Clock size={14} /> Decision Cutoff:
        </span>
        <select
          className="select-input"
          value={filters.decisionCutoff}
          onChange={(e) => onFilterChange({ decisionCutoff: e.target.value })}
        >
          {availableCutoffs.length > 0 ? (
            availableCutoffs.map((c) => (
              <option key={c.time} value={c.time}>
                {c.label}
              </option>
            ))
          ) : (
            <>
              <option value="11:00">11:00 UK Time (Default - EPEX / Nord Pool Day-Ahead Gate)</option>
              <option value="12:00">12:00 UK Time (Auction Results & Secondary)</option>
              <option value="15:30">15:30 UK Time (EPEX GB 15:30 Auction)</option>
              <option value="17:00">17:00 UK Time (Trading Desk Shift Close)</option>
              <option value="23:00">23:00 UK Time (Night Cutoff)</option>
            </>
          )}
        </select>

        <div
          title="Why 11:00 Cutoff? In the UK wholesale electricity market, the primary Day-Ahead auctions (EPEX SPOT and Nord Pool) close bidding at 11:00 UK time on D-1. Any forecast published after 11:00 was unavailable to the procurement trader at gate closure; using later snapshots causes look-ahead bias."
          style={{ cursor: "help", display: "flex", alignItems: "center", color: "var(--accent-cyan)" }}
        >
          <HelpCircle size={16} />
        </div>
      </div>
    </div>
  );
};
