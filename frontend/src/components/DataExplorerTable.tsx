import React, { useState, useMemo } from "react";
import type { MatchedTimeseriesPoint } from "../types";
import { Download, Search, Filter, ChevronLeft, ChevronRight, ArrowUpDown } from "lucide-react";
import { api } from "../services/api";
import type { QueryParams } from "../services/api";

interface DataExplorerTableProps {
  data: MatchedTimeseriesPoint[];
  filters: QueryParams;
  isLoading: boolean;
}

type SortField =
  | "startTime"
  | "generationForecast"
  | "generationActual"
  | "forecastError"
  | "absoluteError"
  | "shortfallMw";

export const DataExplorerTable: React.FC<DataExplorerTableProps> = ({
  data,
  filters,
  isLoading,
}) => {
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [sortField, setSortField] = useState<SortField>("startTime");
  const [sortAsc, setSortAsc] = useState<boolean>(true);
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [pageSize, setPageSize] = useState<number>(25);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false); // default descending for numerical values
    }
  };

  // Filter & Search
  const filteredData = useMemo(() => {
    return data.filter((row) => {
      // Search term
      const matchesSearch =
        row.startTimeLocal?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        row.startTime?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        row.publishTimeLocal?.toLowerCase().includes(searchTerm.toLowerCase());

      if (!matchesSearch) return false;

      // Status Filter
      if (statusFilter === "SHORTFALL") return row.shortfallMw > 0;
      if (statusFilter === "OVERFORECAST") return row.forecastError > 0;
      if (statusFilter === "UNDERFORECAST") return row.forecastError < 0;
      if (statusFilter === "MISSING") return row.status !== "MATCHED";

      return true;
    });
  }, [data, searchTerm, statusFilter]);

  // Sort
  const sortedData = useMemo(() => {
    return [...filteredData].sort((a, b) => {
      let valA: any = a[sortField];
      let valB: any = b[sortField];

      if (valA === undefined || valA === null) valA = 0;
      if (valB === undefined || valB === null) valB = 0;

      if (valA < valB) return sortAsc ? -1 : 1;
      if (valA > valB) return sortAsc ? 1 : -1;
      return 0;
    });
  }, [filteredData, sortField, sortAsc]);

  // Pagination
  const totalPages = Math.ceil(sortedData.length / pageSize) || 1;
  const paginatedData = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return sortedData.slice(start, start + pageSize);
  }, [sortedData, currentPage, pageSize]);

  const exportUrl = api.getExportCsvUrl(filters);

  return (
    <div className="card">
      <div className="card-header">
        <div className="card-title-group">
          <h2 className="card-title">Detailed Delivery Interval Explorer</h2>
          <p className="card-subtitle">
            Searchable, sortable, paginated audit table of matched day-ahead forecast snapshots and actuals
          </p>
        </div>

        {/* CSV Export Button */}
        <a
          href={exportUrl}
          download
          className="btn-primary"
          style={{ textDecoration: "none" }}
          title="Export active filtered dataset to CSV"
        >
          <Download size={14} />
          <span>Export CSV</span>
        </a>
      </div>

      {/* Filter Toolbar */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: "12px",
          marginBottom: "16px",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap" }}>
          {/* Search Box */}
          <div style={{ position: "relative", display: "flex", alignItems: "center" }}>
            <Search size={14} style={{ position: "absolute", left: "10px", color: "var(--text-muted)" }} />
            <input
              type="text"
              placeholder="Search date or snapshot..."
              className="select-input"
              style={{ paddingLeft: "30px", width: "220px" }}
              value={searchTerm}
              onChange={(e) => {
                setSearchTerm(e.target.value);
                setCurrentPage(1);
              }}
            />
          </div>

          {/* Quick Filter */}
          <select
            className="select-input"
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setCurrentPage(1);
            }}
          >
            <option value="ALL">All Intervals ({data.length})</option>
            <option value="SHORTFALL">Shortfall Intervals Only</option>
            <option value="OVERFORECAST">Overforecasts Only</option>
            <option value="UNDERFORECAST">Underforecasts Only</option>
            <option value="MISSING">Missing Data Only</option>
          </select>
        </div>

        {/* Rows per page */}
        <div style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "12px", color: "var(--text-secondary)" }}>
          <span>Show:</span>
          <select
            className="select-input"
            style={{ padding: "4px 8px", fontSize: "12px" }}
            value={pageSize}
            onChange={(e) => {
              setPageSize(Number(e.target.value));
              setCurrentPage(1);
            }}
          >
            <option value={25}>25 rows</option>
            <option value={50}>50 rows</option>
            <option value={100}>100 rows</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="table-responsive">
        <table className="data-table">
          <thead>
            <tr>
              <th onClick={() => handleSort("startTime")} style={{ cursor: "pointer" }}>
                <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                  Delivery Time (UK Local) <ArrowUpDown size={12} />
                </span>
              </th>
              <th>Forecast Published (UK)</th>
              <th>Decision Cutoff</th>
              <th onClick={() => handleSort("generationForecast")} style={{ cursor: "pointer" }}>
                <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                  Forecast (MW) <ArrowUpDown size={12} />
                </span>
              </th>
              <th onClick={() => handleSort("generationActual")} style={{ cursor: "pointer" }}>
                <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                  Actual Outturn (MW) <ArrowUpDown size={12} />
                </span>
              </th>
              <th onClick={() => handleSort("forecastError")} style={{ cursor: "pointer" }}>
                <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                  Forecast Error (MW) <ArrowUpDown size={12} />
                </span>
              </th>
              <th onClick={() => handleSort("absoluteError")} style={{ cursor: "pointer" }}>
                <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                  Absolute Error <ArrowUpDown size={12} />
                </span>
              </th>
              <th onClick={() => handleSort("shortfallMw")} style={{ cursor: "pointer" }}>
                <span style={{ display: "flex", alignItems: "center", gap: "4px" }}>
                  Shortfall (MW) <ArrowUpDown size={12} />
                </span>
              </th>
              <th>Quality Status</th>
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr>
                <td colSpan={9} style={{ textAlign: "center", padding: "40px" }}>
                  Loading table data...
                </td>
              </tr>
            ) : paginatedData.length === 0 ? (
              <tr>
                <td colSpan={9} style={{ textAlign: "center", padding: "40px", color: "var(--text-muted)" }}>
                  No matching records found.
                </td>
              </tr>
            ) : (
              paginatedData.map((row, idx) => {
                const isOver = row.forecastError > 0;
                return (
                  <tr key={idx}>
                    <td><strong>{row.startTimeLocal}</strong></td>
                    <td style={{ color: "var(--text-secondary)" }}>{row.publishTimeLocal}</td>
                    <td style={{ color: "var(--accent-cyan)" }}>{row.decisionCutoffLocal}</td>
                    <td className="num">{row.generationForecast.toLocaleString("en-GB")}</td>
                    <td className="num">{row.generationActual.toLocaleString("en-GB")}</td>
                    <td className="num" style={{ color: isOver ? "var(--accent-rose)" : "var(--accent-cyan)" }}>
                      {row.forecastError > 0 ? `+${row.forecastError.toLocaleString("en-GB")}` : row.forecastError.toLocaleString("en-GB")}
                    </td>
                    <td className="num">{row.absoluteError.toLocaleString("en-GB")}</td>
                    <td className="num" style={{ color: row.shortfallMw > 0 ? "var(--accent-rose)" : "var(--text-muted)", fontWeight: row.shortfallMw > 0 ? 600 : 400 }}>
                      {row.shortfallMw > 0 ? `+${row.shortfallMw.toLocaleString("en-GB")}` : "0"}
                    </td>
                    <td>
                      {row.status === "MATCHED" ? (
                        row.shortfallMw > 0 ? (
                          <span className="badge shortfall">DEFICIT</span>
                        ) : (
                          <span className="badge matched">MATCHED</span>
                        )
                      ) : (
                        <span className="badge missing">{row.status}</span>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      <div className="pagination-bar">
        <span>
          Showing {paginatedData.length > 0 ? (currentPage - 1) * pageSize + 1 : 0} to{" "}
          {Math.min(currentPage * pageSize, sortedData.length)} of {sortedData.length} records
        </span>

        <div className="pagination-controls">
          <button
            className="btn-page"
            disabled={currentPage === 1}
            onClick={() => setCurrentPage(currentPage - 1)}
          >
            <ChevronLeft size={14} />
          </button>
          <span style={{ margin: "0 6px" }}>
            Page {currentPage} of {totalPages}
          </span>
          <button
            className="btn-page"
            disabled={currentPage === totalPages}
            onClick={() => setCurrentPage(currentPage + 1)}
          >
            <ChevronRight size={14} />
          </button>
        </div>
      </div>
    </div>
  );
};
