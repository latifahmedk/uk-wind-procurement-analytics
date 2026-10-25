import pytest
import pandas as pd
import numpy as np
from app.analytics.accuracy import calculate_accuracy_metrics

def test_exact_accuracy_calculations():
    """Verify MAE, RMSE, Mean Bias, and MAPE with verified deterministic numbers."""
    # 4 intervals:
    # 1: Forecast = 1000, Actual = 800  -> Error = +200, Abs = 200
    # 2: Forecast = 1200, Actual = 1500 -> Error = -300, Abs = 300
    # 3: Forecast = 500,  Actual = 500  -> Error = 0,    Abs = 0
    # 4: Forecast = 800,  Actual = 600  -> Error = +200, Abs = 200
    # Sum Error = +100 -> Mean Bias = +25.0 MW
    # Sum Abs Error = 700 -> MAE = 175.0 MW
    # Squared Errors: 40000 + 90000 + 0 + 40000 = 170000 -> Mean = 42500 -> RMSE = sqrt(42500) ≈ 206.16 MW
    matched_df = pd.DataFrame([
        {"status": "MATCHED", "generationForecast": 1000.0, "generationActual": 800.0, "forecastError": 200.0, "absoluteError": 200.0, "deliveryDate": "2026-01-16", "deliveryHour": 0},
        {"status": "MATCHED", "generationForecast": 1200.0, "generationActual": 1500.0, "forecastError": -300.0, "absoluteError": 300.0, "deliveryDate": "2026-01-16", "deliveryHour": 1},
        {"status": "MATCHED", "generationForecast": 500.0, "generationActual": 500.0, "forecastError": 0.0, "absoluteError": 0.0, "deliveryDate": "2026-01-16", "deliveryHour": 2},
        {"status": "MATCHED", "generationForecast": 800.0, "generationActual": 600.0, "forecastError": 200.0, "absoluteError": 200.0, "deliveryDate": "2026-01-16", "deliveryHour": 3},
    ])

    metrics, daily, hourly, distribution = calculate_accuracy_metrics(matched_df)

    assert metrics.mae == 175.0
    assert metrics.rmse == round(float(np.sqrt(42500)), 1)
    assert metrics.meanBias == 25.0
    assert metrics.totalMatchedIntervals == 4
    assert metrics.overforecastCount == 2
    assert metrics.underforecastCount == 1
    assert metrics.overforecastPercentage == 50.0
    assert metrics.underforecastPercentage == 25.0
    assert len(daily) == 1
    assert len(hourly) == 4

def test_mape_excludes_zero_or_near_zero_actuals():
    """Verify that MAPE excludes zero or near-zero observations (< 50 MW) without error."""
    matched_df = pd.DataFrame([
        # Zero actual observation (calm weather shutdown)
        {"status": "MATCHED", "generationForecast": 200.0, "generationActual": 0.0, "forecastError": 200.0, "absoluteError": 200.0},
        # Near zero observation (< 50 MW)
        {"status": "MATCHED", "generationForecast": 150.0, "generationActual": 20.0, "forecastError": 130.0, "absoluteError": 130.0},
        # Valid observation: Forecast = 1100, Actual = 1000 -> 10% error
        {"status": "MATCHED", "generationForecast": 1100.0, "generationActual": 1000.0, "forecastError": 100.0, "absoluteError": 100.0},
        # Valid observation: Forecast = 1800, Actual = 2000 -> 10% error
        {"status": "MATCHED", "generationForecast": 1800.0, "generationActual": 2000.0, "forecastError": -200.0, "absoluteError": 200.0},
    ])

    metrics, _, _, _ = calculate_accuracy_metrics(matched_df)

    assert metrics.totalMatchedIntervals == 4
    assert metrics.excludedZeroActualCount == 2
    assert metrics.validMapeObservations == 2
    # MAPE over valid observations: (10% + 10%) / 2 = 10.0%
    assert metrics.mape == 10.0

def test_interpretation_text_generated():
    """Verify that qualitative interpretation text is generated and reflects computed bias."""
    matched_df = pd.DataFrame([
        {"status": "MATCHED", "generationForecast": 8000.0, "generationActual": 6000.0, "forecastError": 2000.0, "absoluteError": 2000.0},
    ])
    metrics, _, _, _ = calculate_accuracy_metrics(matched_df)
    assert "positive" in metrics.interpretation
    assert "+2000.0 MW" in metrics.interpretation
    assert "overestimating" in metrics.interpretation
