from datetime import datetime, date, timedelta
from typing import List, Dict, Any
import numpy as np
import pandas as pd
from app.utils.time_utils import UTC_TZ

def generate_synthetic_fuelhh(start_date: date, end_date: date) -> List[Dict[str, Any]]:
    """
    Generate synthetic FUELHH generation data for wind.
    UK wind generation typically ranges between 2,000 MW (calm winter high pressure)
    and 18,000+ MW (storm fronts) out of ~28,000 MW total UK wind capacity.
    """
    records = []
    curr = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0, tzinfo=UTC_TZ)
    end = datetime(end_date.year, end_date.month, end_date.day, 23, 30, 0, tzinfo=UTC_TZ)
    
    np.random.seed(42)  # Deterministic for repeatable tests
    base_trend = 10000.0
    
    sp = 1
    curr_date = curr.date()
    
    while curr <= end:
        if curr.date() != curr_date:
            curr_date = curr.date()
            sp = 1
            
        # Diurnal and weather wave variation
        day_offset = (curr.date() - start_date).days
        weather_cycle = np.sin(day_offset * 0.8) * 4500.0
        diurnal_cycle = np.sin((curr.hour + curr.minute / 60.0) / 24.0 * 2 * np.pi) * 1200.0
        noise = np.random.normal(0, 400.0)
        
        gen = max(800.0, min(22000.0, base_trend + weather_cycle + diurnal_cycle + noise))
        
        records.append({
            "dataset": "FUELHH",
            "publishTime": (curr + timedelta(minutes=30)).isoformat().replace("+00:00", "Z"),
            "startTime": curr.isoformat().replace("+00:00", "Z"),
            "settlementDate": curr.strftime("%Y-%m-%d"),
            "settlementPeriod": sp,
            "fuelType": "WIND",
            "generation": round(float(gen), 1),
            "is_synthetic_demo": True
        })
        
        curr += timedelta(minutes=30)
        sp += 1
        
    return records

def generate_synthetic_windfor(start_date: date, end_date: date) -> List[Dict[str, Any]]:
    """
    Generate synthetic WINDFOR forecasts.
    Simulate publication snapshots at standard National Grid ESO hours:
    02:30, 04:30, 07:30, 09:30, 12:25, 15:30, 18:30, 22:30 UTC.
    Each snapshot forecasts up to 72 hours ahead.
    """
    records = []
    np.random.seed(42)
    
    # Decisions are made day-ahead, so forecasts start on start_date - 2 days
    sim_start_date = start_date - timedelta(days=2)
    sim_end_date = end_date + timedelta(days=1)
    
    curr_day = sim_start_date
    snapshot_times = [
        (2, 30), (4, 30), (7, 30), (9, 30),
        (12, 25), (15, 30), (18, 30), (22, 30)
    ]
    
    while curr_day <= sim_end_date:
        for hour, minute in snapshot_times:
            pub_dt = datetime(curr_day.year, curr_day.month, curr_day.day, hour, minute, 0, tzinfo=UTC_TZ)
            
            # Forecast horizon: 0 to 48 hours in 1-hour increments
            for h in range(0, 49):
                target_dt = pub_dt.replace(minute=0, second=0) + timedelta(hours=h)
                
                day_offset = (target_dt.date() - start_date).days
                weather_cycle = np.sin(day_offset * 0.8) * 4500.0
                diurnal_cycle = np.sin((target_dt.hour) / 24.0 * 2 * np.pi) * 1200.0
                
                # Forecast error varies with lead time (uncertainty grows with horizon)
                error_scale = 300.0 + (h * 20.0)
                fc_error = np.random.normal(250.0, error_scale) # Slight positive bias typical in wind forecasting
                
                gen = max(700.0, min(22500.0, 10000.0 + weather_cycle + diurnal_cycle + fc_error))
                
                records.append({
                    "dataset": "WINDFOR",
                    "publishTime": pub_dt.isoformat().replace("+00:00", "Z"),
                    "startTime": target_dt.isoformat().replace("+00:00", "Z"),
                    "generation": round(float(gen), 1),
                    "is_synthetic_demo": True
                })
                
        curr_day += timedelta(days=1)
        
    return records
