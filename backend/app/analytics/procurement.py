import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from app.schemas.analysis import ProcurementInsightPoint, ProcurementAnalysisResponse

OPERATIONAL_DISCLAIMER = (
    "NOTICE FOR PROCUREMENT DESK: This analysis isolates national wind generation volume shortfalls "
    "relative to day-ahead forecasts (Shortfall = max(0, Forecast - Actual)). It does NOT represent "
    "the utility's net commercial deficit or total market procurement requirement. Calculating net commercial "
    "imbalance requires proprietary consumer demand forecasts, retail supplier shaping portfolios, "
    "bilateral forward contracts, and solar/thermal generation assets, which are excluded by specification. "
    "Use these figures strictly as an indicator of wind-induced physical volume variance."
)

def calculate_procurement_insights(matched_df: pd.DataFrame) -> ProcurementAnalysisResponse:
    """
    Generate procurement insight points, wind generation shortfall volume,
    and a conservative P10 downside wind-generation scenario based on historical error volatility.
    """
    if matched_df.empty or "status" not in matched_df.columns:
        return ProcurementAnalysisResponse(
            totalShortfallEnergyMwh=0.0,
            maxShortfallMw=0.0,
            meanShortfallWhenDeficitMw=0.0,
            shortfallIntervalsCount=0,
            shortfallPercentage=0.0,
            downsideMethodology="P10 historical forecast error deduction",
            operationalDisclaimer=OPERATIONAL_DISCLAIMER,
            points=[]
        )
        
    matched = matched_df[matched_df["status"] == "MATCHED"].copy()
    
    if matched.empty:
        return ProcurementAnalysisResponse(
            totalShortfallEnergyMwh=0.0,
            maxShortfallMw=0.0,
            meanShortfallWhenDeficitMw=0.0,
            shortfallIntervalsCount=0,
            shortfallPercentage=0.0,
            downsideMethodology="P10 historical forecast error deduction",
            operationalDisclaimer=OPERATIONAL_DISCLAIMER,
            points=[]
        )
        
    # Calculate 90th percentile of absolute error as historical downside margin
    abs_errors = matched["absoluteError"].dropna().values
    p90_error = float(np.percentile(abs_errors, 90)) if len(abs_errors) > 0 else 500.0
    
    points: List[ProcurementInsightPoint] = []
    shortfalls = []
    
    for _, row in matched.iterrows():
        fc = float(row["generationForecast"])
        act = float(row["generationActual"]) if pd.notna(row["generationActual"]) else None
        
        # Shortfall: max(0, Forecast - Actual)
        shortfall = max(0.0, fc - act) if act is not None else 0.0
        is_shortfall = (shortfall > 1.0) # > 1 MW threshold
        
        # Downside scenario: conservative 10th percentile generation
        downside = max(0.0, fc - p90_error)
        
        if is_shortfall:
            shortfalls.append(shortfall)
            
        points.append(ProcurementInsightPoint(
            startTime=str(row["startTime"]),
            startTimeLocal=str(row.get("startTimeLocal", row["startTime"])),
            generationForecast=round(fc, 1),
            generationActual=round(act, 1) if act is not None else None,
            shortfallMw=round(shortfall, 1),
            isShortfall=is_shortfall,
            downsideScenarioMw=round(downside, 1),
            publishTimeLocal=str(row.get("publishTimeLocal", "")),
            decisionCutoffLocal=str(row.get("decisionCutoffLocal", ""))
        ))
        
    total_shortfall_mwh = sum(shortfalls) # Since intervals are hourly, MW * 1h = MWh
    max_shortfall_mw = max(shortfalls) if shortfalls else 0.0
    mean_shortfall_deficit = float(np.mean(shortfalls)) if shortfalls else 0.0
    shortfall_intervals = len(shortfalls)
    shortfall_pct = round((shortfall_intervals / len(matched)) * 100.0, 1)
    
    downside_methodology = (
        f"The downside scenario reflects a conservative P10 wind yield (Forecast minus {p90_error:.0f} MW, "
        f"representing the 90th percentile historical forecast deviation across matched intervals). "
        f"This indicates the minimum generation volume likely to clear with 90% statistical confidence."
    )
    
    return ProcurementAnalysisResponse(
        totalShortfallEnergyMwh=round(total_shortfall_mwh, 1),
        maxShortfallMw=round(max_shortfall_mw, 1),
        meanShortfallWhenDeficitMw=round(mean_shortfall_deficit, 1),
        shortfallIntervalsCount=shortfall_intervals,
        shortfallPercentage=shortfall_pct,
        downsideMethodology=downside_methodology,
        operationalDisclaimer=OPERATIONAL_DISCLAIMER,
        points=points
    )
