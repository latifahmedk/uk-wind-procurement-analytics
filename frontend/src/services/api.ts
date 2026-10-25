import axios from "axios";
import type {
  MetadataResponse,
  ExecutiveSummaryKpis,
  AccuracyResponse,
  MatchedTimeseriesPoint,
  ProcurementAnalysisResponse,
  HealthResponse,
} from "../types";

// Configurable API base URL with fallback to local backend or relative in production
const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Accept": "application/json",
  },
});

export interface QueryParams {
  startDate: string;
  endDate: string;
  filterBy: "delivery_date" | "decision_date";
  decisionCutoff: string;
}

export const api = {
  getHealth: async (): Promise<HealthResponse> => {
    const res = await apiClient.get<HealthResponse>("/health");
    return res.data;
  },

  getMetadata: async (): Promise<MetadataResponse> => {
    const res = await apiClient.get<MetadataResponse>("/metadata");
    return res.data;
  },

  getSummary: async (params: QueryParams): Promise<ExecutiveSummaryKpis> => {
    const res = await apiClient.get<ExecutiveSummaryKpis>("/analysis/summary", { params });
    return res.data;
  },

  getAccuracy: async (params: QueryParams): Promise<AccuracyResponse> => {
    const res = await apiClient.get<AccuracyResponse>("/analysis/accuracy", { params });
    return res.data;
  },

  getTimeseries: async (params: QueryParams): Promise<MatchedTimeseriesPoint[]> => {
    const res = await apiClient.get<MatchedTimeseriesPoint[]>("/analysis/timeseries", { params });
    return res.data;
  },

  getProcurement: async (params: QueryParams): Promise<ProcurementAnalysisResponse> => {
    const res = await apiClient.get<ProcurementAnalysisResponse>("/analysis/procurement", { params });
    return res.data;
  },

  getExportCsvUrl: (params: QueryParams): string => {
    const query = new URLSearchParams({
      startDate: params.startDate,
      endDate: params.endDate,
      filterBy: params.filterBy,
      decisionCutoff: params.decisionCutoff,
    });
    return `${API_BASE_URL}/data/export?${query.toString()}`;
  },
};
