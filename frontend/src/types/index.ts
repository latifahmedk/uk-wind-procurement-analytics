export interface CutoffOption {
  time: string;
  label: string;
  description: string;
}

export interface DatasetInfo {
  name: string;
  endpoint: string;
  description: string;
  documentedUnits: string;
  fields: string[];
}

export interface MetadataResponse {
  projectName: string;
  version: string;
  timezone: string;
  datasets: DatasetInfo[];
  supportedDateRangeMin: string;
  supportedDateRangeMax: string;
  defaultDateRangeStart: string;
  defaultDateRangeEnd: string;
  defaultCutoff: string;
  availableCutoffs: CutoffOption[];
  dataFreshnessStatus: string;
  lastRefreshUtc: string;
  isDemoData: boolean;
  dataLimitationsNotice: string;
}

export interface ExecutiveSummaryKpis {
  latestEligibleForecastMw: number | null;
  selectedDecisionCutoff: string;
  totalForecastEnergyGwh: number;
  totalActualEnergyGwh: number;
  maeMw: number;
  rmseMw: number;
  meanBiasMw: number;
  totalMatchedObservations: number;
  totalShortfallEnergyGwh: number;
  maxShortfallMw: number;
  overforecastRatePct: number;
  underforecastRatePct: number;
  dataFreshness: string;
  dataSource: string;
  isDemoData: boolean;
  lastRefreshUtc: string;
}

export interface AccuracyMetrics {
  mae: number;
  rmse: number;
  meanBias: number;
  mape: number | null;
  validMapeObservations: number;
  excludedZeroActualCount: number;
  totalMatchedIntervals: number;
  missingForecastIntervals: number;
  missingActualIntervals: number;
  overforecastCount: number;
  overforecastPercentage: number;
  underforecastCount: number;
  underforecastPercentage: number;
  interpretation: string;
}

export interface DailyAccuracy {
  date: string;
  mae: number;
  rmse: number;
  meanBias: number;
  forecastEnergyMwh: number;
  actualEnergyMwh: number;
  energyVarianceMwh: number;
  maxOverforecastMw: number;
  maxUnderforecastMw: number;
  matchedIntervals: number;
}

export interface HourlyBiasProfile {
  hour: number;
  meanBias: number;
  meanForecast: number;
  meanActual: number;
  mae: number;
  observationCount: number;
}

export interface ErrorDistributionBucket {
  rangeLabel: string;
  minVal: number;
  maxVal: number;
  count: number;
  percentage: number;
}

export interface AccuracyResponse {
  metrics: AccuracyMetrics;
  daily: DailyAccuracy[];
  hourly: HourlyBiasProfile[];
  distribution: ErrorDistributionBucket[];
}

export interface MatchedTimeseriesPoint {
  startTime: string;
  startTimeLocal: string;
  deliveryDate: string;
  deliveryHour: number;
  generationForecast: number;
  generationActual: number;
  forecastError: number;
  absoluteError: number;
  publishTime: string;
  publishTimeLocal: string;
  decisionCutoffLocal: string;
  shortfallMw: number;
  status: "MATCHED" | "MISSING_ACTUAL" | "MISSING_FORECAST";
}

export interface ProcurementInsightPoint {
  startTime: string;
  startTimeLocal: string;
  generationForecast: number;
  generationActual: number | null;
  shortfallMw: number;
  isShortfall: boolean;
  downsideScenarioMw: number;
  publishTimeLocal: string;
  decisionCutoffLocal: string;
}

export interface ProcurementAnalysisResponse {
  totalShortfallEnergyMwh: number;
  maxShortfallMw: number;
  meanShortfallWhenDeficitMw: number;
  shortfallIntervalsCount: number;
  shortfallPercentage: number;
  downsideMethodology: string;
  operationalDisclaimer: string;
  points: ProcurementInsightPoint[];
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  timestampUtc: string;
  upstreamElexonApi: {
    status: string;
    code: number;
    message?: string;
  };
}
