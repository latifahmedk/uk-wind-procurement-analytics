import React, { useState, useEffect, useCallback } from "react";
import { Header } from "./components/Header";
import { Navigation } from "./components/Navigation";
import type { TabType } from "./components/Navigation";
import { ControlsBar } from "./components/ControlsBar";
import { KpiGrid } from "./components/KpiGrid";
import { ForecastActualChart } from "./components/ForecastActualChart";
import { AccuracySection } from "./components/AccuracySection";
import { ProcurementInsightsPanel } from "./components/ProcurementInsightsPanel";
import { DataExplorerTable } from "./components/DataExplorerTable";
import { api } from "./services/api";
import type { QueryParams } from "./services/api";
import type {
  MetadataResponse,
  ExecutiveSummaryKpis,
  AccuracyResponse,
  MatchedTimeseriesPoint,
  ProcurementAnalysisResponse,
} from "./types";
import { AlertCircle, RefreshCw } from "lucide-react";

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>("overview");
  const [filters, setFilters] = useState<QueryParams>({
    startDate: "2026-01-01",
    endDate: "2026-01-31",
    filterBy: "delivery_date",
    decisionCutoff: "11:00",
  });

  const [metadata, setMetadata] = useState<MetadataResponse | null>(null);
  const [kpis, setKpis] = useState<ExecutiveSummaryKpis | null>(null);
  const [accuracy, setAccuracy] = useState<AccuracyResponse | null>(null);
  const [timeseries, setTimeseries] = useState<MatchedTimeseriesPoint[]>([]);
  const [procurement, setProcurement] = useState<ProcurementAnalysisResponse | null>(null);

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Initial load: metadata
  useEffect(() => {
    const loadMetadata = async () => {
      try {
        const meta = await api.getMetadata();
        setMetadata(meta);
      } catch (err) {
        console.warn("Could not load metadata from API:", err);
      }
    };
    loadMetadata();
  }, []);

  // Fetch all analytics datasets
  const fetchDashboardData = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Parallel requests for optimal loading speed
      const [summaryRes, accuracyRes, timeseriesRes, procurementRes] = await Promise.all([
        api.getSummary(filters),
        api.getAccuracy(filters),
        api.getTimeseries(filters),
        api.getProcurement(filters),
      ]);

      setKpis(summaryRes);
      setAccuracy(accuracyRes);
      setTimeseries(timeseriesRes);
      setProcurement(procurementRes);
    } catch (err: any) {
      console.error("Dashboard fetch error:", err);
      setError(
        err.response?.data?.message ||
        err.message ||
        "Failed to communicate with the analytics backend. Please verify that the backend server is running."
      );
    } finally {
      setIsLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  const handleFilterChange = (newFilters: Partial<QueryParams>) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
  };

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <Navigation activeTab={activeTab} onTabChange={setActiveTab} />

      {/* Main Terminal Area */}
      <div className="main-wrapper">
        <Header
          kpis={kpis}
          isLoading={isLoading}
          onRefresh={fetchDashboardData}
        />

        <ControlsBar
          filters={filters}
          onFilterChange={handleFilterChange}
          availableCutoffs={metadata?.availableCutoffs}
        />

        <main className="content-body">
          {/* Error Banner */}
          {error && (
            <div
              style={{
                backgroundColor: "rgba(244, 63, 94, 0.15)",
                border: "1px solid var(--accent-rose)",
                borderRadius: "var(--radius-md)",
                padding: "16px 20px",
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                gap: "12px",
                color: "#F87171",
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                <AlertCircle size={20} />
                <span>{error}</span>
              </div>
              <button
                className="btn-secondary"
                onClick={fetchDashboardData}
                style={{ borderColor: "var(--accent-rose)", color: "#FFFFFF" }}
              >
                <RefreshCw size={14} /> Retry
              </button>
            </div>
          )}

          {/* TAB 1: EXECUTIVE OVERVIEW */}
          {activeTab === "overview" && (
            <>
              <KpiGrid kpis={kpis} isLoading={isLoading} />
              <ForecastActualChart timeseriesData={timeseries} isLoading={isLoading} />
              {accuracy && <AccuracySection accuracyData={accuracy} isLoading={isLoading} />}
              {procurement && (
                <ProcurementInsightsPanel procurementData={procurement} isLoading={isLoading} />
              )}
            </>
          )}

          {/* TAB 2: FORECAST VS ACTUAL */}
          {activeTab === "forecast" && (
            <>
              <KpiGrid kpis={kpis} isLoading={isLoading} />
              <ForecastActualChart timeseriesData={timeseries} isLoading={isLoading} />
              <DataExplorerTable data={timeseries} filters={filters} isLoading={isLoading} />
            </>
          )}

          {/* TAB 3: ACCURACY ANALYSIS */}
          {activeTab === "accuracy" && (
            <AccuracySection accuracyData={accuracy} isLoading={isLoading} />
          )}

          {/* TAB 4: PROCUREMENT INSIGHTS */}
          {activeTab === "procurement" && (
            <ProcurementInsightsPanel procurementData={procurement} isLoading={isLoading} />
          )}

          {/* TAB 5: DATA EXPLORER & CSV EXPORT */}
          {activeTab === "explorer" && (
            <DataExplorerTable data={timeseries} filters={filters} isLoading={isLoading} />
          )}
        </main>
      </div>
    </div>
  );
};

export default App;
