import pytest
import pandas as pd
from datetime import datetime, timezone
from app.services.forecast_selector import select_day_ahead_forecasts

def test_select_latest_forecast_before_cutoff():
    """
    Verify that among multiple snapshots published before the cutoff,
    the latest snapshot is selected, and snapshots published after are excluded.
    """
    # Delivery interval: 2026-01-16 00:00:00 UTC (Local date = 2026-01-16)
    # Decision date = 2026-01-15. Default cutoff = 11:00 UK Time (11:00 UTC)
    raw_forecasts = [
        # Eligible snapshots on 2026-01-15
        {"startTime": "2026-01-16T00:00:00Z", "publishTime": "2026-01-15T02:30:00Z", "generation": 7000.0},
        {"startTime": "2026-01-16T00:00:00Z", "publishTime": "2026-01-15T07:30:00Z", "generation": 7200.0},
        {"startTime": "2026-01-16T00:00:00Z", "publishTime": "2026-01-15T09:30:00Z", "generation": 7472.0}, # Latest before 11:00
        # Ineligible snapshots published AFTER 11:00 cutoff (Look-ahead bias!)
        {"startTime": "2026-01-16T00:00:00Z", "publishTime": "2026-01-15T12:25:00Z", "generation": 7800.0},
        {"startTime": "2026-01-16T00:00:00Z", "publishTime": "2026-01-15T15:30:00Z", "generation": 8100.0},
    ]

    deliv_start = datetime(2026, 1, 16, 0, 0, 0, tzinfo=timezone.utc)
    deliv_end = datetime(2026, 1, 16, 23, 59, 59, tzinfo=timezone.utc)

    selected_df, meta = select_day_ahead_forecasts(
        raw_forecasts=raw_forecasts,
        deliv_start_utc=deliv_start,
        deliv_end_utc=deliv_end,
        cutoff_time_str="11:00"
    )

    assert len(selected_df) == 1
    row = selected_df.iloc[0]
    # Must select 09:30 snapshot with 7472.0 MW
    assert row["publishTime"] == "2026-01-15T09:30:00Z"
    assert row["generationForecast"] == 7472.0
    assert bool(row["isEligible"]) is True
    # Verify post-cutoff snapshots were counted as excluded
    assert meta["excluded_post_cutoff_snapshots"] == 2

def test_prevent_look_ahead_bias():
    """Verify that if all available forecasts are published after the cutoff, none are selected."""
    raw_forecasts = [
        {"startTime": "2026-01-16T00:00:00Z", "publishTime": "2026-01-15T14:00:00Z", "generation": 8000.0},
        {"startTime": "2026-01-16T00:00:00Z", "publishTime": "2026-01-15T18:00:00Z", "generation": 8200.0},
    ]
    deliv_start = datetime(2026, 1, 16, 0, 0, 0, tzinfo=timezone.utc)
    deliv_end = datetime(2026, 1, 16, 23, 59, 59, tzinfo=timezone.utc)

    selected_df, meta = select_day_ahead_forecasts(
        raw_forecasts=raw_forecasts,
        deliv_start_utc=deliv_start,
        deliv_end_utc=deliv_end,
        cutoff_time_str="11:00"
    )
    assert selected_df.empty
    assert meta["excluded_post_cutoff_snapshots"] == 2

def test_handle_duplicate_forecast_records():
    """Verify that identical duplicate rows from upstream streaming are properly deduplicated."""
    raw_forecasts = [
        {"startTime": "2026-01-16T00:00:00Z", "publishTime": "2026-01-15T09:30:00Z", "generation": 7500.0},
        {"startTime": "2026-01-16T00:00:00Z", "publishTime": "2026-01-15T09:30:00Z", "generation": 7500.0}, # Duplicate
    ]
    deliv_start = datetime(2026, 1, 16, 0, 0, 0, tzinfo=timezone.utc)
    deliv_end = datetime(2026, 1, 16, 23, 59, 59, tzinfo=timezone.utc)

    selected_df, meta = select_day_ahead_forecasts(
        raw_forecasts=raw_forecasts,
        deliv_start_utc=deliv_start,
        deliv_end_utc=deliv_end,
        cutoff_time_str="11:00"
    )
    assert len(selected_df) == 1
    assert selected_df.iloc[0]["generationForecast"] == 7500.0

def test_configurable_decision_cutoff():
    """Verify that changing decision cutoff from 11:00 to 17:00 allows afternoon snapshots."""
    raw_forecasts = [
        {"startTime": "2026-01-16T00:00:00Z", "publishTime": "2026-01-15T09:30:00Z", "generation": 7472.0},
        {"startTime": "2026-01-16T00:00:00Z", "publishTime": "2026-01-15T15:30:00Z", "generation": 7685.0},
    ]
    deliv_start = datetime(2026, 1, 16, 0, 0, 0, tzinfo=timezone.utc)
    deliv_end = datetime(2026, 1, 16, 23, 59, 59, tzinfo=timezone.utc)

    # With 17:00 cutoff, 15:30 snapshot becomes eligible and preferred
    selected_df, meta = select_day_ahead_forecasts(
        raw_forecasts=raw_forecasts,
        deliv_start_utc=deliv_start,
        deliv_end_utc=deliv_end,
        cutoff_time_str="17:00"
    )
    assert len(selected_df) == 1
    assert selected_df.iloc[0]["publishTime"] == "2026-01-15T15:30:00Z"
    assert selected_df.iloc[0]["generationForecast"] == 7685.0
