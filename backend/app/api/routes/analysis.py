from fastapi import APIRouter, Query
from typing import List, Dict, Any
from app.services.orchestrator import analytics_orchestrator
from app.analytics.accuracy import calculate_accuracy_metrics
from app.analytics.procurement import calculate_procurement_insights
from app.schemas.analysis import (
    ExecutiveSummaryKpis, AccuracyMetrics, DailyAccuracy,
    HourlyBiasProfile, ErrorDistributionBucket, MatchedTimeseriesPoint,
    ProcurementAnalysisResponse
)

router = APIRouter(prefix="/analysis", tags=["Analysis"])

@router.get("/summary", response_model=ExecutiveSummaryKpis)
async def get_analysis_summary(
    startDate: str = Query("2026-01-01", description="Start date YYYY-MM-DD"),
    endDate: str = Query("2026-01-31", description="End date YYYY-MM-DD"),
    filterBy: str = Query("delivery_date", description="'delivery_date' or 'decision_date'"),
    decisionCutoff: str = Query("11:00", description="Cutoff time in UK local time HH:MM")
):
    """Returns top-level executive KPI metrics for the requested period and cutoff."""
    bundle = await analytics_orchestrator.get_bundle(
        start_date_str=startDate,
        end_date_str=endDate,
        filter_by=filterBy,
        decision_cutoff=decisionCutoff
    )
    return analytics_orchestrator.build_executive_kpis(bundle)

@router.get("/accuracy")
async def get_accuracy_analysis(
    startDate: str = Query("2026-01-01", description="Start date YYYY-MM-DD"),
    endDate: str = Query("2026-01-31", description="End date YYYY-MM-DD"),
    filterBy: str = Query("delivery_date", description="'delivery_date' or 'decision_date'"),
    decisionCutoff: str = Query("11:00", description="Cutoff time in UK local time HH:MM")
):
    """
    Returns quantitative forecast accuracy metrics (MAE, RMSE, Mean Bias, valid MAPE),
    daily breakdown, hourly bias profile, and error distribution.
    """
    bundle = await analytics_orchestrator.get_bundle(
        start_date_str=startDate,
        end_date_str=endDate,
        filter_by=filterBy,
        decision_cutoff=decisionCutoff
    )
    metrics, daily, hourly, distribution = calculate_accuracy_metrics(bundle.matched_df)
    return {
        "metrics": metrics,
        "daily": daily,
        "hourly": hourly,
        "distribution": distribution
    }

@router.get("/timeseries", response_model=List[MatchedTimeseriesPoint])
async def get_timeseries_analysis(
    startDate: str = Query("2026-01-01", description="Start date YYYY-MM-DD"),
    endDate: str = Query("2026-01-31", description="End date YYYY-MM-DD"),
    filterBy: str = Query("delivery_date", description="'delivery_date' or 'decision_date'"),
    decisionCutoff: str = Query("11:00", description="Cutoff time in UK local time HH:MM")
):
    """
    Returns matched forecast vs actual time series points with delivery timestamps,
    publication snapshots, individual error values, and shortfall indicators.
    """
    bundle = await analytics_orchestrator.get_bundle(
        start_date_str=startDate,
        end_date_str=endDate,
        filter_by=filterBy,
        decision_cutoff=decisionCutoff
    )
    df = bundle.matched_df
    if df.empty:
        return []
    
    # Fill defaults for missing values
    records = []
    for _, row in df.iterrows():
        records.append(MatchedTimeseriesPoint(
            startTime=str(row["startTime"]),
            startTimeLocal=str(row.get("startTimeLocal", row["startTime"])),
            deliveryDate=str(row.get("deliveryDate", "")),
            deliveryHour=int(row.get("deliveryHour", 0)),
            generationForecast=round(float(row["generationForecast"]), 1) if pd.notna(row.get("generationForecast")) else 0.0,
            generationActual=round(float(row["generationActual"]), 1) if pd.notna(row.get("generationActual")) else 0.0,
            forecastError=round(float(row["forecastError"]), 1) if pd.notna(row.get("forecastError")) else 0.0,
            absoluteError=round(float(row["absoluteError"]), 1) if pd.notna(row.get("absoluteError")) else 0.0,
            publishTime=str(row.get("publishTime", "")),
            publishTimeLocal=str(row.get("publishTimeLocal", "")),
            decisionCutoffLocal=str(row.get("decisionCutoffLocal", "")),
            shortfallMw=round(float(row["shortfallMw"]), 1) if pd.notna(row.get("shortfallMw")) else 0.0,
            status=str(row.get("status", "MATCHED"))
        ))
    return records

import pandas as pd

@router.get("/procurement", response_model=ProcurementAnalysisResponse)
async def get_procurement_insights(
    startDate: str = Query("2026-01-01", description="Start date YYYY-MM-DD"),
    endDate: str = Query("2026-01-31", description="End date YYYY-MM-DD"),
    filterBy: str = Query("delivery_date", description="'delivery_date' or 'decision_date'"),
    decisionCutoff: str = Query("11:00", description="Cutoff time in UK local time HH:MM")
):
    """
    Returns wind shortfall volumes, peak shortfalls, downside P10 scenario,
    and operational procurement disclaimers.
    """
    bundle = await analytics_orchestrator.get_bundle(
        start_date_str=startDate,
        end_date_str=endDate,
        filter_by=filterBy,
        decision_cutoff=decisionCutoff
    )
    return calculate_procurement_insights(bundle.matched_df)
