import React from "react";
import {
  LayoutDashboard,
  LineChart,
  Target,
  AlertTriangle,
  TableProperties,
  Wind,
  Info
} from "lucide-react";

export type TabType = "overview" | "forecast" | "accuracy" | "procurement" | "explorer";

interface NavigationProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
}

export const Navigation: React.FC<NavigationProps> = ({ activeTab, onTabChange }) => {
  const navItems: { id: TabType; label: string; icon: React.ReactNode }[] = [
    { id: "overview", label: "Executive Overview", icon: <LayoutDashboard size={18} /> },
    { id: "forecast", label: "Forecast vs Actual", icon: <LineChart size={18} /> },
    { id: "accuracy", label: "Forecast Accuracy", icon: <Target size={18} /> },
    { id: "procurement", label: "Procurement Insights", icon: <AlertTriangle size={18} /> },
    { id: "explorer", label: "Data Explorer & Export", icon: <TableProperties size={18} /> },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="brand-icon">
          <Wind size={22} color="#FFFFFF" />
        </div>
        <div>
          <div className="brand-title">UK Energy Analytics</div>
          <div className="brand-subtitle">DAY-AHEAD DESK</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <button
            key={item.id}
            className={`nav-item ${activeTab === item.id ? "active" : ""}`}
            onClick={() => onTabChange(item.id)}
          >
            <span className="nav-icon">{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="status-row">
          <span>Market:</span>
          <strong style={{ color: "var(--text-primary)" }}>GB Wholesale</strong>
        </div>
        <div className="status-row">
          <span>Provider:</span>
          <strong style={{ color: "var(--accent-cyan)" }}>Elexon BMRS</strong>
        </div>
        <div className="status-row">
          <span>Resolution:</span>
          <span style={{ fontFamily: "var(--font-mono)" }}>30m / 1h Avg</span>
        </div>
        <div style={{ marginTop: "10px", fontSize: "10px", color: "var(--text-muted)", lineHeight: 1.4 }}>
          Day-Ahead Procurement Pilot for January 2026 Cohorts
        </div>
      </div>
    </aside>
  );
};
