from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo
from typing import Tuple
import pandas as pd

UK_TZ = ZoneInfo("Europe/London")
UTC_TZ = ZoneInfo("UTC")

def parse_iso_to_utc(iso_str: str) -> datetime:
    """Parse an ISO 8601 string to a timezone-aware UTC datetime."""
    dt = pd.to_datetime(iso_str)
    if dt.tz is None:
        return dt.tz_localize("UTC").to_pydatetime()
    return dt.tz_convert("UTC").to_pydatetime()

def to_uk_local_str(dt: datetime, fmt: str = "%Y-%m-%d %H:%M %Z") -> str:
    """Format a datetime into UK local time (Europe/London)."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC_TZ)
    local_dt = dt.astimezone(UK_TZ)
    return local_dt.strftime(fmt)

def get_decision_cutoff_utc(delivery_dt: datetime, cutoff_time_str: str = "11:00") -> datetime:
    """
    Given a delivery datetime (in UTC or local), determine the applicable Day-Ahead
    procurement decision cutoff in UTC.
    
    Business Logic:
    1. Determine the delivery date D in UK local time (Europe/London).
    2. Decision date is D - 1 day.
    3. Construct decision datetime on (D - 1) at cutoff_time_str in UK local time.
    4. Convert that local decision datetime to UTC.
    
    Example:
    Delivery interval: 2026-01-16 00:00:00 UTC (Local date = 2026-01-16)
    Decision date = 2026-01-15
    Cutoff: 11:00 Europe/London -> 2026-01-15 11:00:00 UTC (in winter GMT)
    """
    if delivery_dt.tzinfo is None:
        delivery_dt = delivery_dt.replace(tzinfo=UTC_TZ)
        
    local_delivery = delivery_dt.astimezone(UK_TZ)
    delivery_date = local_delivery.date()
    decision_date = delivery_date - timedelta(days=1)
    
    # Parse cutoff time
    parts = cutoff_time_str.strip().split(":")
    hour = int(parts[0])
    minute = int(parts[1]) if len(parts) > 1 else 0
    
    local_cutoff = datetime(
        decision_date.year, decision_date.month, decision_date.day,
        hour, minute, 0, tzinfo=UK_TZ
    )
    
    return local_cutoff.astimezone(UTC_TZ)

def get_delivery_date_for_decision_date(decision_date: date) -> date:
    """For a given procurement decision date D_dec, delivery date is D_dec + 1 day."""
    return decision_date + timedelta(days=1)

def get_date_range_bounds(
    start_date: date,
    end_date: date,
    filter_by: str = "delivery_date",
    cutoff_time_str: str = "11:00"
) -> Tuple[datetime, datetime, datetime, datetime]:
    """
    Returns (actuals_start_utc, actuals_end_utc, forecasts_pub_start_utc, forecasts_pub_end_utc).
    
    Carefully handles the January 2026 boundary:
    If filter_by == 'decision_date':
      User requested decisions made from start_date to end_date.
      Delivery dates are start_date + 1 day to end_date + 1 day (e.g. Jan 31 decision delivers Feb 1!).
      Forecast publication window needs to cover decision cutoffs for these dates.
      
    If filter_by == 'delivery_date':
      User requested generation delivered from start_date to end_date.
      Decisions were made from start_date - 1 day to end_date - 1 day (e.g. Jan 1 delivery was decided Dec 31!).
    """
    if filter_by == "decision_date":
        deliv_start_date = start_date + timedelta(days=1)
        deliv_end_date = end_date + timedelta(days=1)
        
        # Delivery span in UTC
        deliv_start_utc = datetime(deliv_start_date.year, deliv_start_date.month, deliv_start_date.day, 0, 0, 0, tzinfo=UTC_TZ)
        deliv_end_utc = datetime(deliv_end_date.year, deliv_end_date.month, deliv_end_date.day, 23, 59, 59, tzinfo=UTC_TZ)
        
        # Forecasts published from start_date - 1 day (to capture earliest snapshots) up to end_date at cutoff
        pub_start_utc = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0, tzinfo=UTC_TZ) - timedelta(days=1)
        # Latest cutoff on end_date
        latest_cutoff = get_decision_cutoff_utc(deliv_end_utc, cutoff_time_str)
        pub_end_utc = latest_cutoff + timedelta(hours=2) # buffer
        
    else:  # delivery_date
        deliv_start_utc = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0, tzinfo=UTC_TZ)
        deliv_end_utc = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59, tzinfo=UTC_TZ)
        
        dec_start_date = start_date - timedelta(days=1)
        dec_end_date = end_date - timedelta(days=1)
        
        pub_start_utc = datetime(dec_start_date.year, dec_start_date.month, dec_start_date.day, 0, 0, 0, tzinfo=UTC_TZ) - timedelta(days=1)
        latest_cutoff = get_decision_cutoff_utc(deliv_end_utc, cutoff_time_str)
        pub_end_utc = latest_cutoff + timedelta(hours=2)
        
    return deliv_start_utc, deliv_end_utc, pub_start_utc, pub_end_utc
