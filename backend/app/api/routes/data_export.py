from fastapi import APIRouter, Query, Response
import io
import csv
import pandas as pd
from app.services.orchestrator import analytics_orchestrator

router = APIRouter(prefix="/data", tags=["Data Export"])

@router.get("/export")
async def export_data_csv(
    startDate: str = Query("2026-01-01", description="Start date YYYY-MM-DD"),
    endDate: str = Query("2026-01-31", description="End date YYYY-MM-DD"),
    filterBy: str = Query("delivery_date", description="'delivery_date' or 'decision_date'"),
    decisionCutoff: str = Query("11:00", description="Cutoff time in UK local time HH:MM")
):
    """
    Export matched forecast and actual records to CSV using the exact active filters
    and forecast-selection cutoff policy.
    """
    bundle = await analytics_orchestrator.get_bundle(
        start_date_str=startDate,
        end_date_str=endDate,
        filter_by=filterBy,
        decision_cutoff=decisionCutoff
    )
    df = bundle.matched_df
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        "Delivery Date (UK)",
        "Delivery Interval Start (UK Local)",
        "Delivery Interval Start (UTC)",
        "Selected Forecast Published (UK Local)",
        "Selected Forecast Published (UTC)",
        "Applicable Decision Cutoff",
        "Forecast Generation (MW)",
        "Actual Generation Outturn (MW)",
        "Forecast Error (MW)",
        "Absolute Error (MW)",
        "Wind Generation Shortfall (MW)",
        "Quality Status"
    ])
    
    if not df.empty:
        for _, row in df.iterrows():
            writer.writerow([
                row.get("deliveryDate", ""),
                row.get("startTimeLocal", ""),
                row.get("startTime", ""),
                row.get("publishTimeLocal", ""),
                row.get("publishTime", ""),
                row.get("decisionCutoffLocal", ""),
                f"{float(row['generationForecast']):.1f}" if pd.notna(row.get("generationForecast")) else "",
                f"{float(row['generationActual']):.1f}" if pd.notna(row.get("generationActual")) else "",
                f"{float(row['forecastError']):.1f}" if pd.notna(row.get("forecastError")) else "",
                f"{float(row['absoluteError']):.1f}" if pd.notna(row.get("absoluteError")) else "",
                f"{float(row['shortfallMw']):.1f}" if pd.notna(row.get("shortfallMw")) else "",
                row.get("status", "MATCHED")
            ])
            
    csv_content = output.getvalue()
    filename = f"uk_wind_day_ahead_procurement_{startDate}_{endDate}_cutoff_{decisionCutoff.replace(':', '')}.csv"
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}",
            "Cache-Control": "no-cache"
        }
    )
