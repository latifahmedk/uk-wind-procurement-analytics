import pytest
from datetime import datetime, date, timezone
from zoneinfo import ZoneInfo
from app.utils.time_utils import (
    get_decision_cutoff_utc,
    get_date_range_bounds,
    get_delivery_date_for_decision_date,
    UK_TZ, UTC_TZ
)

def test_decision_cutoff_calculation_gmt():
    """In winter (GMT / UTC+0), 11:00 UK local time is 11:00 UTC on D-1."""
    delivery_dt = datetime(2026, 1, 16, 0, 0, 0, tzinfo=UTC_TZ)
    cutoff_utc = get_decision_cutoff_utc(delivery_dt, cutoff_time_str="11:00")
    
    assert cutoff_utc.year == 2026
    assert cutoff_utc.month == 1
    assert cutoff_utc.day == 15
    assert cutoff_utc.hour == 11
    assert cutoff_utc.minute == 0
    assert cutoff_utc.tzinfo == UTC_TZ

def test_decision_cutoff_calculation_bst():
    """In summer (BST / UTC+1), 11:00 UK local time is 10:00 UTC on D-1."""
    delivery_dt = datetime(2026, 7, 16, 12, 0, 0, tzinfo=UTC_TZ)
    cutoff_utc = get_decision_cutoff_utc(delivery_dt, cutoff_time_str="11:00")
    
    assert cutoff_utc.year == 2026
    assert cutoff_utc.month == 7
    assert cutoff_utc.day == 15
    assert cutoff_utc.hour == 10  # 11:00 BST is 10:00 UTC
    assert cutoff_utc.minute == 0

def test_month_boundary_decision_date_to_delivery_date():
    """
    Requirement 5: A decision made on 2026-01-31 delivers on 2026-02-01.
    Must not exclude records crossing the month boundary.
    """
    decision_date = date(2026, 1, 31)
    delivery_date = get_delivery_date_for_decision_date(decision_date)
    assert delivery_date == date(2026, 2, 1)

def test_date_range_bounds_for_cohorts():
    """Verify bounds for delivery_date and decision_date filtering."""
    # 1. Delivery date filtering: Jan 1 to Jan 31
    deliv_start, deliv_end, pub_start, pub_end = get_date_range_bounds(
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
        filter_by="delivery_date",
        cutoff_time_str="11:00"
    )
    assert deliv_start.date() == date(2026, 1, 1)
    assert deliv_end.date() == date(2026, 1, 31)
    # Publication window must start before Dec 31 to capture forecasts for Jan 1 delivery
    assert pub_start.date() <= date(2025, 12, 31)

    # 2. Decision date filtering: Jan 1 to Jan 31
    deliv_start2, deliv_end2, pub_start2, pub_end2 = get_date_range_bounds(
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 31),
        filter_by="decision_date",
        cutoff_time_str="11:00"
    )
    # Decision Jan 1 delivers Jan 2; Decision Jan 31 delivers Feb 1
    assert deliv_start2.date() == date(2026, 1, 2)
    assert deliv_end2.date() == date(2026, 2, 1)
