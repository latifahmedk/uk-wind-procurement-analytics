import pytest
import pandas as pd
from datetime import datetime, timezone
from app.analytics.matcher import match_forecast_and_actuals

def test_match_forecast_and_hourly_actuals():
    """Verify that half-hourly FUELHH actuals are properly averaged into hourly outturn and matched."""
    # Forecast for 2026-01-16 00:00:00 UTC
    selected_fc_df = pd.DataFrame([{
        "startTime": "2026-01-16T00:00:00Z",
        "startTimeLocal": "2026-01-16 00:00 GMT",
        "publishTime": "2026-01-15T09:30:00Z",
        "publishTimeLocal": "2026-01-15 09:30 GMT",
        "generationForecast": 8000.0,
        "cutoffTimeUtc": "2026-01-15T11:00:00Z",
        "cutoffTimeLocal": "2026-01-15 11:00 GMT",
        "leadTimeHours": 14.5,
        "isEligible": True
    }])

    # Two 30-min settlement periods in hour 00:00: 7000 MW and 6000 MW -> Average = 6500 MW
    raw_actuals = [
        {"startTime": "2026-01-16T00:00:00Z", "generation": 7000.0, "settlementPeriod": 1, "fuelType": "WIND"},
        {"startTime": "2026-01-16T00:30:00Z", "generation": 6000.0, "settlementPeriod": 2, "fuelType": "WIND"},
    ]

    deliv_start = datetime(2026, 1, 16, 0, 0, 0, tzinfo=timezone.utc)
    deliv_end = datetime(2026, 1, 16, 23, 59, 59, tzinfo=timezone.utc)

    matched_df, summary = match_forecast_and_actuals(
        selected_forecasts_df=selected_fc_df,
        raw_actuals=raw_actuals,
        deliv_start_utc=deliv_start,
        deliv_end_utc=deliv_end
    )

    assert len(matched_df) == 1
    row = matched_df.iloc[0]
    assert row["status"] == "MATCHED"
    assert row["generationForecast"] == 8000.0
    assert row["generationActual"] == 6500.0
    # Forecast Error = Forecast - Actual = 8000 - 6500 = +1500 MW (Overforecast)
    assert row["forecastError"] == 1500.0
    assert row["absoluteError"] == 1500.0
    # Shortfall = max(0, 8000 - 6500) = 1500.0 MW
    assert row["shortfallMw"] == 1500.0
    assert summary["matched_count"] == 1

def test_missing_forecast_and_missing_actual_statuses():
    """Verify handling when forecast or actual is missing."""
    selected_fc_df = pd.DataFrame([{
        "startTime": "2026-01-16T00:00:00Z",
        "generationForecast": 7000.0,
    }])

    # Actual is for hour 01:00:00, not 00:00:00
    raw_actuals = [
        {"startTime": "2026-01-16T01:00:00Z", "generation": 6500.0, "settlementPeriod": 3, "fuelType": "WIND"},
    ]

    deliv_start = datetime(2026, 1, 16, 0, 0, 0, tzinfo=timezone.utc)
    deliv_end = datetime(2026, 1, 16, 23, 59, 59, tzinfo=timezone.utc)

    matched_df, summary = match_forecast_and_actuals(
        selected_forecasts_df=selected_fc_df,
        raw_actuals=raw_actuals,
        deliv_start_utc=deliv_start,
        deliv_end_utc=deliv_end
    )

    statuses = set(matched_df["status"].tolist())
    assert "MISSING_ACTUAL" in statuses
    assert "MISSING_FORECAST" in statuses
    assert summary["missing_actual_count"] == 1
    assert summary["missing_forecast_count"] == 1
