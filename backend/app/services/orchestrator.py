from datetime import datetime, date, timedelta
from typing import Dict, Any, Tuple
import pandas as pd
from app.core.config import settings
from app.core.logging import logger
from app.utils.time_utils import get_date_range_bounds, parse_iso_to_utc, to_uk_local_str
from app.services.elexon_client import elexon_client
from app.services.forecast_selector import select_day_ahead_forecasts
from app.analytics.matcher import match_forecast_and_actuals
from app.analytics.accuracy import calculate_accuracy_metrics
from app.analytics.procurement import calculate_procurement_insights
from app.schemas.analysis import ExecutiveSummaryKpis

class AnalyzedDatasetBundle:
    def __init__(
        self,
        matched_df: pd.DataFrame,
        selected_forecasts_df: pd.DataFrame,
        raw_actuals: list,
        is_demo: bool,
        deliv_start_utc: datetime,
        deliv_end_utc: datetime,
        cutoff_applied: str,
        filter_by: str,
        selection_meta: dict,
        matching_meta: dict
    ):
        self.matched_df = matched_df
        self.selected_forecasts_df = selected_forecasts_df
        self.raw_actuals = raw_actuals
        self.is_demo = is_demo
        self.deliv_start_utc = deliv_start_utc
        self.deliv_end_utc = deliv_end_utc
        self.cutoff_applied = cutoff_applied
        self.filter_by = filter_by
        self.selection_meta = selection_meta
        self.matching_meta = matching_meta

class AnalyticsOrchestrator:
    def __init__(self):
        self._bundle_cache = {}

    async def get_bundle(
        self,
        start_date_str: str = "2026-01-01",
        end_date_str: str = "2026-01-31",
        filter_by: str = "delivery_date",
        decision_cutoff: str = "11:00",
        force_refresh: bool = False
    ) -> AnalyzedDatasetBundle:
        cache_key = f"{start_date_str}_{end_date_str}_{filter_by}_{decision_cutoff}"
        if not force_refresh and cache_key in self._bundle_cache:
            return self._bundle_cache[cache_key]

        start_d = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_d = datetime.strptime(end_date_str, "%Y-%m-%d").date()

        # Resolve exact temporal window and decision cutoff bounds
        deliv_start_utc, deliv_end_utc, pub_start_utc, pub_end_utc = get_date_range_bounds(
            start_date=start_d,
            end_date=end_d,
            filter_by=filter_by,
            cutoff_time_str=decision_cutoff
        )

        logger.info(
            f"Orchestrator fetching: Delivery window [{deliv_start_utc} - {deliv_end_utc}], "
            f"Forecast Pub window [{pub_start_utc} - {pub_end_utc}], Cutoff [{decision_cutoff}]"
        )

        # 1. Fetch actuals for the delivery window
        deliv_start_date = deliv_start_utc.date()
        deliv_end_date = deliv_end_utc.date()
        actuals_records, act_is_demo = await elexon_client.fetch_fuelhh(deliv_start_date, deliv_end_date)

        # 2. Fetch raw wind forecasts for the publication window
        forecast_records, fc_is_demo = await elexon_client.fetch_windfor(pub_start_utc, pub_end_utc)

        is_demo = act_is_demo or fc_is_demo

        # 3. Apply critical forecast selection logic: latest available snapshot <= cutoff
        selected_fc_df, sel_meta = select_day_ahead_forecasts(
            raw_forecasts=forecast_records,
            deliv_start_utc=deliv_start_utc,
            deliv_end_utc=deliv_end_utc,
            cutoff_time_str=decision_cutoff
        )

        # 4. Match with FUELHH actuals
        matched_df, match_meta = match_forecast_and_actuals(
            selected_forecasts_df=selected_fc_df,
            raw_actuals=actuals_records,
            deliv_start_utc=deliv_start_utc,
            deliv_end_utc=deliv_end_utc
        )

        bundle = AnalyzedDatasetBundle(
            matched_df=matched_df,
            selected_forecasts_df=selected_fc_df,
            raw_actuals=actuals_records,
            is_demo=is_demo,
            deliv_start_utc=deliv_start_utc,
            deliv_end_utc=deliv_end_utc,
            cutoff_applied=decision_cutoff,
            filter_by=filter_by,
            selection_meta=sel_meta,
            matching_meta=match_meta
        )

        self._bundle_cache[cache_key] = bundle
        return bundle

    def build_executive_kpis(self, bundle: AnalyzedDatasetBundle) -> ExecutiveSummaryKpis:
        matched = bundle.matched_df
        metrics, _, _, _ = calculate_accuracy_metrics(matched)
        proc = calculate_procurement_insights(matched)

        # Calculate totals
        if not matched.empty and "generationForecast" in matched.columns:
            valid_fc = matched["generationForecast"].dropna()
            total_fc_gwh = round(float(valid_fc.sum()) / 1000.0, 2)
            latest_fc = float(valid_fc.iloc[-1]) if len(valid_fc) > 0 else None
        else:
            total_fc_gwh = 0.0
            latest_fc = None

        if not matched.empty and "generationActual" in matched.columns:
            valid_act = matched["generationActual"].dropna()
            total_act_gwh = round(float(valid_act.sum()) / 1000.0, 2)
        else:
            total_act_gwh = 0.0

        total_shortfall_gwh = round(proc.totalShortfallEnergyMwh / 1000.0, 2)

        data_freshness = "ILLUSTRATIVE_DEMO" if bundle.is_demo else "LIVE_ELEXON"

        return ExecutiveSummaryKpis(
            latestEligibleForecastMw=latest_fc,
            selectedDecisionCutoff=f"{bundle.cutoff_applied} Europe/London (D-1)",
            totalForecastEnergyGwh=total_fc_gwh,
            totalActualEnergyGwh=total_act_gwh,
            maeMw=metrics.mae,
            rmseMw=metrics.rmse,
            meanBiasMw=metrics.meanBias,
            totalMatchedObservations=metrics.totalMatchedIntervals,
            totalShortfallEnergyGwh=total_shortfall_gwh,
            maxShortfallMw=proc.maxShortfallMw,
            overforecastRatePct=metrics.overforecastPercentage,
            underforecastRatePct=metrics.underforecastPercentage,
            dataFreshness=data_freshness,
            dataSource="Elexon Insights Solution (BMRS API) FUELHH & WINDFOR",
            isDemoData=bundle.is_demo,
            lastRefreshUtc=datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        )

analytics_orchestrator = AnalyticsOrchestrator()
