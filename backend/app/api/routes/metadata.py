from fastapi import APIRouter
from datetime import datetime
from app.core.config import settings
from app.schemas.metadata import MetadataResponse, DatasetInfo, CutoffOption

router = APIRouter(tags=["Metadata"])

@router.get("/metadata", response_model=MetadataResponse)
async def get_metadata():
    """Returns dataset metadata, market gate closures, supported date boundaries, and units."""
    return MetadataResponse(
        projectName=settings.PROJECT_NAME,
        version=settings.VERSION,
        timezone="Europe/London (UK Local Time)",
        datasets=[
            DatasetInfo(
                name="FUELHH",
                endpoint="/datasets/FUELHH/stream",
                description="Half-hourly generation outturn by fuel type across Great Britain. Filtered strictly to fuelType=WIND.",
                documentedUnits="MW (Megawatts average over 30-min settlement period)",
                fields=["startTime", "settlementDate", "settlementPeriod", "fuelType", "generation"]
            ),
            DatasetInfo(
                name="WINDFOR",
                endpoint="/datasets/WINDFOR/stream",
                description="Wind generation forecast published in snapshot intervals by National Grid ESO via Elexon BMRS.",
                documentedUnits="MW (Megawatts average over hourly delivery intervals)",
                fields=["startTime", "publishTime", "generation"]
            )
        ],
        supportedDateRangeMin="2024-01-01",
        supportedDateRangeMax="2026-02-05",
        defaultDateRangeStart="2026-01-01",
        defaultDateRangeEnd="2026-01-31",
        defaultCutoff=settings.DEFAULT_DECISION_CUTOFF,
        availableCutoffs=[
            CutoffOption(
                time="11:00",
                label="11:00 UK Time (Default - EPEX / Nord Pool Day-Ahead Gate Closure)",
                description="Main Great Britain wholesale Day-Ahead auction gate closure (EPEX SPOT GB & Nord Pool GB Day-Ahead Auctions close at 11:00 GMT/BST on D-1)."
            ),
            CutoffOption(
                time="12:00",
                label="12:00 UK Time (Auction Results & Secondary Window)",
                description="Post-auction clearing window following preliminary day-ahead market settlement."
            ),
            CutoffOption(
                time="15:30",
                label="15:30 UK Time (EPEX GB 15:30 Auction Gate Closure)",
                description="Afternoon day-ahead reference auction gate closure for peak and off-peak shaping."
            ),
            CutoffOption(
                time="17:00",
                label="17:00 UK Time (Desk End-of-Day Shift Close)",
                description="Standard conclusion of day-ahead energy trading desk core trading operations."
            ),
            CutoffOption(
                time="23:00",
                label="23:00 UK Time (Night Gate Closure / Final Day-Ahead)",
                description="Final pre-midnight day-ahead position lock before delivery day intraday operations begin."
            )
        ],
        dataFreshnessStatus="OPERATIONAL",
        lastRefreshUtc=datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        isDemoData=False,
        dataLimitationsNotice=(
            "Analysis strictly uses official Elexon BMRS generation data. Consumer demand forecasts, "
            "solar generation, and utility contract positions are intentionally excluded per requirements."
        )
    )
