import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Tuple
from app.utils.time_utils import to_uk_local_str, UK_TZ, UTC_TZ

def match_forecast_and_actuals(
    selected_forecasts_df: pd.DataFrame,
    raw_actuals: List[Dict[str, Any]],
    deliv_start_utc: datetime,
    deliv_end_utc: datetime
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Match selected day-ahead forecasts with FUELHH actual generation outturn.
    
    Domain Resolution Handling:
    - FUELHH actuals are reported at half-hourly settlement periods (e.g. 00:00, 00:30).
    - Elexon WINDFOR forecasts are published at hourly intervals (e.g. 00:00, 01:00).
    - To provide an accurate physical comparison, FUELHH actuals are aggregated to
      hourly average MW (mean of the two 30-minute settlement periods within each hour),
      matching the hourly average power forecast by National Grid ESO.
    """
    if selected_forecasts_df.empty or not raw_actuals:
        empty_df = pd.DataFrame()
        return empty_df, {
            "matched_count": 0,
            "missing_forecast_count": 0,
            "missing_actual_count": 0
        }
        
    df_act = pd.DataFrame(raw_actuals)
    df_act["startTime_dt"] = pd.to_datetime(df_act["startTime"], utc=True)
    df_act["generation"] = pd.to_numeric(df_act["generation"], errors="coerce")
    
    # Filter actuals to delivery range
    df_act = df_act[(df_act["startTime_dt"] >= deliv_start_utc) & (df_act["startTime_dt"] <= deliv_end_utc)]
    
    # Group FUELHH into hourly average MW
    df_act["hour_dt"] = df_act["startTime_dt"].dt.floor("h")
    df_act_hourly = df_act.groupby("hour_dt")["generation"].agg(["mean", "count"]).reset_index()
    df_act_hourly = df_act_hourly.rename(columns={"mean": "generationActual", "count": "actual_sp_count"})
    df_act_hourly["startTime"] = df_act_hourly["hour_dt"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Selected forecasts
    df_fc = selected_forecasts_df.copy()
    if "startTime_dt" not in df_fc.columns:
        df_fc["startTime_dt"] = pd.to_datetime(df_fc["startTime"], utc=True)
        
    # Merge on startTime
    merged = pd.merge(df_fc, df_act_hourly, on="startTime", how="outer", suffixes=("_fc", "_act"))
    
    # Determine startTime_dt from either side
    merged["startTime_dt"] = merged["startTime_dt"].fillna(merged["hour_dt"])
    merged = merged.sort_values("startTime_dt").reset_index(drop=True)
    
    # Flag statuses
    def assign_status(row):
        if pd.isna(row.get("generationForecast")):
            return "MISSING_FORECAST"
        if pd.isna(row.get("generationActual")):
            return "MISSING_ACTUAL"
        return "MATCHED"
        
    merged["status"] = merged.apply(assign_status, axis=1)
    
    # Calculate errors for matched rows
    matched_mask = merged["status"] == "MATCHED"
    
    merged["forecastError"] = np.nan
    merged["absoluteError"] = np.nan
    merged["shortfallMw"] = np.nan
    
    merged.loc[matched_mask, "forecastError"] = (
        merged.loc[matched_mask, "generationForecast"] - merged.loc[matched_mask, "generationActual"]
    ).round(1)
    
    merged.loc[matched_mask, "absoluteError"] = (
        merged.loc[matched_mask, "forecastError"].abs()
    ).round(1)
    
    # Wind Shortfall: When actual generation < forecast, shortfall is (Forecast - Actual). Otherwise 0.
    merged.loc[matched_mask, "shortfallMw"] = (
        merged.loc[matched_mask, "forecastError"].apply(lambda e: max(0.0, float(e)))
    ).round(1)
    
    # Fill in date / hour fields
    merged["deliveryDate"] = merged["startTime_dt"].dt.tz_convert(UK_TZ).dt.strftime("%Y-%m-%d")
    merged["deliveryHour"] = merged["startTime_dt"].dt.tz_convert(UK_TZ).dt.hour
    merged["startTimeLocal"] = merged["startTime_dt"].dt.tz_convert(UK_TZ).dt.strftime("%Y-%m-%d %H:%M %Z")
    
    summary = {
        "total_intervals": len(merged),
        "matched_count": int(matched_mask.sum()),
        "missing_forecast_count": int((merged["status"] == "MISSING_FORECAST").sum()),
        "missing_actual_count": int((merged["status"] == "MISSING_ACTUAL").sum())
    }
    
    return merged, summary
