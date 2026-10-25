from fastapi import APIRouter, Query
from typing import List, Optional
from datetime import datetime
import pandas as pd
from app.services.orchestrator import analytics_orchestrator
from app.schemas.actual import ActualRecord
from app.utils.time_utils import to_uk_local_str, UK_TZ

router = APIRouter(tags=["Actuals"])

@router.get("/actuals", response_model=List[ActualRecord])
async def get_actuals(
    startDate: str = Query("2026-01-01", description="Start date YYYY-MM-DD"),
    endDate: str = Query("2026-01-31", description="End date YYYY-MM-DD"),
    resolution: str = Query("hourly_avg", description="'hourly_avg' or 'half_hourly'")
):
    """
    Retrieve actual wind generation outturn (FUELHH filtered to fuelType=WIND)
    at hourly average or half-hourly settlement period resolution.
    """
    bundle = await analytics_orchestrator.get_bundle(
        start_date_str=startDate,
        end_date_str=endDate,
        filter_by="delivery_date"
    )
    raw_actuals = bundle.raw_actuals
    if not raw_actuals:
        return []
        
    df = pd.DataFrame(raw_actuals)
    df["startTime_dt"] = pd.to_datetime(df["startTime"], utc=True)
    df["generation"] = pd.to_numeric(df["generation"], errors="coerce")
    
    # Filter to requested delivery bounds
    start_dt = datetime.strptime(startDate, "%Y-%m-%d").replace(tzinfo=UK_TZ)
    end_dt = datetime.strptime(endDate, "%Y-%m-%d").replace(hour=23, minute=59, second=59, tzinfo=UK_TZ)
    df = df[(df["startTime_dt"] >= start_dt) & (df["startTime_dt"] <= end_dt)]
    
    if resolution == "half_hourly":
        records = []
        for _, row in df.sort_values("startTime_dt").iterrows():
            st_local = row["startTime_dt"].tz_convert(UK_TZ).strftime("%Y-%m-%d %H:%M %Z")
            records.append(ActualRecord(
                startTime=row["startTime_dt"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                startTimeLocal=st_local,
                settlementDate=str(row.get("settlementDate")),
                settlementPeriod=int(row.get("settlementPeriod", 0)),
                fuelType="WIND",
                generationActual=round(float(row["generation"]), 1)
            ))
        return records
    else:
        # Default: hourly average
        df["hour_dt"] = df["startTime_dt"].dt.floor("h")
        grouped = df.groupby("hour_dt")["generation"].mean().reset_index()
        records = []
        for _, row in grouped.sort_values("hour_dt").iterrows():
            st_local = row["hour_dt"].tz_convert(UK_TZ).strftime("%Y-%m-%d %H:%M %Z")
            records.append(ActualRecord(
                startTime=row["hour_dt"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                startTimeLocal=st_local,
                settlementDate=row["hour_dt"].tz_convert(UK_TZ).strftime("%Y-%m-%d"),
                settlementPeriod=None,
                fuelType="WIND",
                generationActual=round(float(row["generation"]), 1)
            ))
        return records
