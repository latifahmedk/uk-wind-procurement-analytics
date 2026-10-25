import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from app.utils.time_utils import get_decision_cutoff_utc, to_uk_local_str, parse_iso_to_utc, UK_TZ, UTC_TZ
from app.core.logging import logger

def select_day_ahead_forecasts(
    raw_forecasts: List[Dict[str, Any]],
    deliv_start_utc: datetime,
    deliv_end_utc: datetime,
    cutoff_time_str: str = "11:00"
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Select the latest eligible day-ahead wind generation forecast published on or before
    the procurement decision cutoff for each delivery interval.
    
    Prevents look-ahead bias by strictly enforcing publishTime <= decision_cutoff.
    """
    if not raw_forecasts:
        empty_df = pd.DataFrame(columns=[
            "startTime", "startTimeLocal", "publishTime", "publishTimeLocal",
            "generationForecast", "cutoffTimeUtc", "cutoffTimeLocal",
            "leadTimeHours", "isEligible"
        ])
        return empty_df, {"total_raw_forecasts": 0, "selected_intervals_count": 0, "excluded_post_cutoff_snapshots": 0}
        
    df = pd.DataFrame(raw_forecasts)
    
    # Standardize column types
    df["startTime_dt"] = pd.to_datetime(df["startTime"], utc=True)
    df["publishTime_dt"] = pd.to_datetime(df["publishTime"], utc=True)
    df["generation"] = pd.to_numeric(df["generation"], errors="coerce")
    
    # Filter to requested delivery range
    df = df[(df["startTime_dt"] >= deliv_start_utc) & (df["startTime_dt"] <= deliv_end_utc)]
    if df.empty:
        empty_df = pd.DataFrame(columns=[
            "startTime", "startTimeLocal", "publishTime", "publishTimeLocal",
            "generationForecast", "cutoffTimeUtc", "cutoffTimeLocal",
            "leadTimeHours", "isEligible"
        ])
        return empty_df, {"total_raw_forecasts": len(raw_forecasts), "selected_intervals_count": 0, "excluded_post_cutoff_snapshots": 0}
        
    # Deduplicate exact duplicate records if upstream API streams duplicates
    df = df.drop_duplicates(subset=["startTime_dt", "publishTime_dt", "generation"])
    
    # Calculate applicable decision cutoff for each row's delivery interval
    # Cache cutoffs by unique delivery dates to avoid redundant calls
    unique_dates = df["startTime_dt"].dt.tz_convert(UK_TZ).dt.date.unique()
    date_cutoff_map = {}
    for d in unique_dates:
        sample_dt = datetime(d.year, d.month, d.day, 12, 0, 0, tzinfo=UK_TZ)
        cutoff_utc = get_decision_cutoff_utc(sample_dt, cutoff_time_str)
        date_cutoff_map[d] = cutoff_utc
        
    # Assign cutoff_dt to every row based on delivery date
    df["delivery_date_local"] = df["startTime_dt"].dt.tz_convert(UK_TZ).dt.date
    df["cutoff_utc"] = df["delivery_date_local"].map(date_cutoff_map)
    
    # Filter: ONLY forecasts published ON OR BEFORE the decision cutoff
    eligible_mask = df["publishTime_dt"] <= df["cutoff_utc"]
    excluded_post_cutoff_count = int((~eligible_mask).sum())
    
    df_eligible = df[eligible_mask].copy()
    
    if df_eligible.empty:
        logger.warning(f"No forecasts found on or before {cutoff_time_str} cutoff for window.")
        empty_df = pd.DataFrame(columns=[
            "startTime", "startTimeLocal", "publishTime", "publishTimeLocal",
            "generationForecast", "cutoffTimeUtc", "cutoffTimeLocal",
            "leadTimeHours", "isEligible"
        ])
        return empty_df, {
            "total_raw_forecasts": len(raw_forecasts),
            "selected_intervals_count": 0,
            "excluded_post_cutoff_snapshots": excluded_post_cutoff_count,
            "cutoff_applied": cutoff_time_str,
            "earliest_selected_publish": None,
            "latest_selected_publish": None
        }
        
    # CRITICAL SELECTION: For each delivery interval (startTime_dt), select the record with LATEST publishTime_dt
    # Sort by startTime_dt ascending, then publishTime_dt descending
    df_eligible = df_eligible.sort_values(by=["startTime_dt", "publishTime_dt"], ascending=[True, False])
    
    # Drop duplicates keeping the first (which has max publishTime_dt)
    df_selected = df_eligible.drop_duplicates(subset=["startTime_dt"], keep="first").copy()
    
    # Calculate lead time (hours between forecast publication and delivery start)
    df_selected["leadTimeHours"] = (
        (df_selected["startTime_dt"] - df_selected["publishTime_dt"]).dt.total_seconds() / 3600.0
    ).round(2)
    
    # Formatted columns
    df_selected["startTime"] = df_selected["startTime_dt"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    df_selected["startTimeLocal"] = df_selected["startTime_dt"].dt.tz_convert(UK_TZ).dt.strftime("%Y-%m-%d %H:%M %Z")
    df_selected["publishTime"] = df_selected["publishTime_dt"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    df_selected["publishTimeLocal"] = df_selected["publishTime_dt"].dt.tz_convert(UK_TZ).dt.strftime("%Y-%m-%d %H:%M %Z")
    df_selected["generationForecast"] = df_selected["generation"].round(1)
    df_selected["cutoffTimeUtc"] = df_selected["cutoff_utc"].dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    df_selected["cutoffTimeLocal"] = df_selected["cutoff_utc"].dt.tz_convert(UK_TZ).dt.strftime("%Y-%m-%d %H:%M %Z")
    df_selected["isEligible"] = True
    
    result_df = df_selected[[
        "startTime", "startTimeLocal", "publishTime", "publishTimeLocal",
        "generationForecast", "cutoffTimeUtc", "cutoffTimeLocal",
        "leadTimeHours", "isEligible"
    ]].sort_values("startTime").reset_index(drop=True)
    
    metadata = {
        "total_raw_forecasts": len(raw_forecasts),
        "selected_intervals_count": len(result_df),
        "excluded_post_cutoff_snapshots": excluded_post_cutoff_count,
        "cutoff_applied": cutoff_time_str,
        "earliest_selected_publish": result_df["publishTime"].min() if not result_df.empty else None,
        "latest_selected_publish": result_df["publishTime"].max() if not result_df.empty else None
    }
    
    return result_df, metadata
