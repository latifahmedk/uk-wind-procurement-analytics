from fastapi import APIRouter, Query
from typing import List, Optional
from app.services.orchestrator import analytics_orchestrator
from app.schemas.forecast import SelectedForecastRecord

router = APIRouter(tags=["Forecasts"])

@router.get("/forecasts", response_model=List[SelectedForecastRecord])
async def get_selected_forecasts(
    startDate: str = Query("2026-01-01", description="Start date YYYY-MM-DD"),
    endDate: str = Query("2026-01-31", description="End date YYYY-MM-DD"),
    filterBy: str = Query("delivery_date", description="'delivery_date' or 'decision_date'"),
    decisionCutoff: str = Query("11:00", description="Cutoff time in UK local time HH:MM")
):
    """
    Retrieve eligible day-ahead wind generation forecasts selected strictly on or before
    the specified decision cutoff (D-1 at configured cutoff time), preventing look-ahead bias.
    """
    bundle = await analytics_orchestrator.get_bundle(
        start_date_str=startDate,
        end_date_str=endDate,
        filter_by=filterBy,
        decision_cutoff=decisionCutoff
    )
    df = bundle.selected_forecasts_df
    if df.empty:
        return []
    return [SelectedForecastRecord(**row) for row in df.to_dict(orient="records")]
