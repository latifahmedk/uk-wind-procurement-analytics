import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from app.schemas.analysis import (
    AccuracyMetrics, DailyAccuracy, HourlyBiasProfile, ErrorDistributionBucket
)

def calculate_accuracy_metrics(matched_df: pd.DataFrame) -> Tuple[AccuracyMetrics, List[DailyAccuracy], List[HourlyBiasProfile], List[ErrorDistributionBucket]]:
    """
    Calculate comprehensive forecast accuracy metrics, daily breakdowns,
    hourly bias profiles, and error distribution histograms.
    """
    if matched_df.empty or "status" not in matched_df.columns:
        empty_metrics = AccuracyMetrics(
            mae=0.0, rmse=0.0, meanBias=0.0, mape=None,
            validMapeObservations=0, excludedZeroActualCount=0,
            totalMatchedIntervals=0, missingForecastIntervals=0, missingActualIntervals=0,
            overforecastCount=0, overforecastPercentage=0.0,
            underforecastCount=0, underforecastPercentage=0.0,
            interpretation="No matched data available for the requested period."
        )
        return empty_metrics, [], [], []
        
    matched = matched_df[matched_df["status"] == "MATCHED"].copy()
    total_matched = len(matched)
    missing_fc = int((matched_df["status"] == "MISSING_FORECAST").sum())
    missing_act = int((matched_df["status"] == "MISSING_ACTUAL").sum())
    
    if total_matched == 0:
        empty_metrics = AccuracyMetrics(
            mae=0.0, rmse=0.0, meanBias=0.0, mape=None,
            validMapeObservations=0, excludedZeroActualCount=0,
            totalMatchedIntervals=0,
            missingForecastIntervals=missing_fc,
            missingActualIntervals=missing_act,
            overforecastCount=0, overforecastPercentage=0.0,
            underforecastCount=0, underforecastPercentage=0.0,
            interpretation="Zero intervals could be matched between forecast and actual generation."
        )
        return empty_metrics, [], [], []
        
    errors = matched["forecastError"].values
    abs_errors = matched["absoluteError"].values
    forecasts = matched["generationForecast"].values
    actuals = matched["generationActual"].values
    
    # 1. MAE
    mae = float(np.mean(abs_errors))
    
    # 2. RMSE
    rmse = float(np.sqrt(np.mean(errors ** 2)))
    
    # 3. Mean Error (Bias)
    mean_bias = float(np.mean(errors))
    
    # 4. MAPE (excluding zero or near-zero actuals < 50 MW to prevent infinite distortion)
    mape_threshold = 50.0  # MW
    valid_mape_mask = actuals > mape_threshold
    valid_mape_count = int(valid_mape_mask.sum())
    excluded_zero_count = int((~valid_mape_mask).sum())
    
    mape: Optional[float] = None
    if valid_mape_count > 0:
        pct_errors = np.abs(forecasts[valid_mape_mask] - actuals[valid_mape_mask]) / actuals[valid_mape_mask] * 100.0
        mape = round(float(np.mean(pct_errors)), 2)
        
    # 5. Overforecast / Underforecast counts
    overforecast_mask = errors > 0.0
    underforecast_mask = errors < 0.0
    over_count = int(overforecast_mask.sum())
    under_count = int(underforecast_mask.sum())
    over_pct = round((over_count / total_matched) * 100.0, 1)
    under_pct = round((under_count / total_matched) * 100.0, 1)
    
    # 6. Qualitative Automated Interpretation
    bias_desc = "overestimating" if mean_bias > 50 else ("underestimating" if mean_bias < -50 else "neutral on average with balanced")
    rmse_mae_ratio = rmse / mae if mae > 0 else 1.0
    tail_risk_desc = "significant tail risk from severe ramp forecasting spikes" if rmse_mae_ratio > 1.35 else "consistent error variance without extreme outliers"
    
    interpretation = (
        f"Across {total_matched} matched intervals, the day-ahead wind forecast exhibited a "
        f"{'positive' if mean_bias >= 0 else 'negative'} mean bias of {mean_bias:+.1f} MW, "
        f"{bias_desc} actual generation in {over_pct}% of delivery intervals. "
        f"The Mean Absolute Error (MAE) of {mae:.1f} MW alongside an RMSE of {rmse:.1f} MW "
        f"(RMSE/MAE ratio: {rmse_mae_ratio:.2f}) indicates {tail_risk_desc}. "
        f"{'Caution: Overforecast bias directly increases the likelihood of uncontracted procurement deficits in balancing timescales.' if mean_bias > 0 else 'Underforecasting provides an operational buffer against deficit, but may lead to surplus spill or discount sell-back in cashout.'}"
    )
    
    metrics = AccuracyMetrics(
        mae=round(mae, 1),
        rmse=round(rmse, 1),
        meanBias=round(mean_bias, 1),
        mape=mape,
        validMapeObservations=valid_mape_count,
        excludedZeroActualCount=excluded_zero_count,
        totalMatchedIntervals=total_matched,
        missingForecastIntervals=missing_fc,
        missingActualIntervals=missing_act,
        overforecastCount=over_count,
        overforecastPercentage=over_pct,
        underforecastCount=under_count,
        underforecastPercentage=under_pct,
        interpretation=interpretation
    )
    
    # 7. Daily Accuracy Breakdown
    daily_list: List[DailyAccuracy] = []
    if "deliveryDate" in matched.columns:
        grouped_daily = matched.groupby("deliveryDate")
        for date_str, group in grouped_daily:
            d_err = group["forecastError"].values
            d_abs_err = group["absoluteError"].values
            d_fc = group["generationForecast"].values
            d_act = group["generationActual"].values
            
            d_mae = float(np.mean(d_abs_err))
            d_rmse = float(np.sqrt(np.mean(d_err ** 2)))
            d_bias = float(np.mean(d_err))
            
            # Energy MWh = sum of hourly average MW * 1h
            fc_mwh = float(np.sum(d_fc))
            act_mwh = float(np.sum(d_act))
            var_mwh = fc_mwh - act_mwh
            
            max_over = float(np.max(d_err)) if len(d_err) > 0 and np.max(d_err) > 0 else 0.0
            max_under = float(np.min(d_err)) if len(d_err) > 0 and np.min(d_err) < 0 else 0.0
            
            daily_list.append(DailyAccuracy(
                date=str(date_str),
                mae=round(d_mae, 1),
                rmse=round(d_rmse, 1),
                meanBias=round(d_bias, 1),
                forecastEnergyMwh=round(fc_mwh, 1),
                actualEnergyMwh=round(act_mwh, 1),
                energyVarianceMwh=round(var_mwh, 1),
                maxOverforecastMw=round(max_over, 1),
                maxUnderforecastMw=round(abs(max_under), 1),
                matchedIntervals=len(group)
            ))
            
    daily_list.sort(key=lambda x: x.date)
    
    # 8. Hourly Bias Profile
    hourly_list: List[HourlyBiasProfile] = []
    if "deliveryHour" in matched.columns:
        grouped_hourly = matched.groupby("deliveryHour")
        for hour_num, group in grouped_hourly:
            h_err = group["forecastError"].values
            h_abs_err = group["absoluteError"].values
            h_fc = group["generationForecast"].values
            h_act = group["generationActual"].values
            
            hourly_list.append(HourlyBiasProfile(
                hour=int(hour_num),
                meanBias=round(float(np.mean(h_err)), 1),
                meanForecast=round(float(np.mean(h_fc)), 1),
                meanActual=round(float(np.mean(h_act)), 1),
                mae=round(float(np.mean(h_abs_err)), 1),
                observationCount=len(group)
            ))
    hourly_list.sort(key=lambda x: x.hour)
    
    # 9. Error Distribution Buckets
    buckets = [
        ("< -2000 MW", -1e9, -2000.0),
        ("-2000 to -1000 MW", -2000.0, -1000.0),
        ("-1000 to -250 MW", -1000.0, -250.0),
        ("-250 to +250 MW (Near Zero)", -250.0, 250.0),
        ("+250 to +1000 MW", 250.0, 1000.0),
        ("+1000 to +2000 MW", 1000.0, 2000.0),
        ("> +2000 MW", 2000.0, 1e9),
    ]
    
    distribution_list: List[ErrorDistributionBucket] = []
    for label, min_v, max_v in buckets:
        mask = (errors >= min_v) & (errors < max_v)
        b_count = int(mask.sum())
        b_pct = round((b_count / total_matched) * 100.0, 1) if total_matched > 0 else 0.0
        distribution_list.append(ErrorDistributionBucket(
            rangeLabel=label,
            minVal=min_v if min_v > -1e8 else -3000.0,
            maxVal=max_v if max_v < 1e8 else 3000.0,
            count=b_count,
            percentage=b_pct
        ))
        
    return metrics, daily_list, hourly_list, distribution_list
