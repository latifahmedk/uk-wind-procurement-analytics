from pydantic import BaseModel, Field
from typing import Optional

class ActualRecord(BaseModel):
    startTime: str = Field(..., description="Target delivery interval start time (ISO 8601 UTC)")
    startTimeLocal: str = Field(..., description="Target delivery interval start time in UK local time")
    settlementDate: Optional[str] = Field(None, description="UK settlement date YYYY-MM-DD")
    settlementPeriod: Optional[int] = Field(None, description="Settlement period (1-48, or 50 on clock change)")
    fuelType: str = Field("WIND", description="Generation fuel type (filtered to WIND)")
    generationActual: float = Field(..., description="Actual wind generation outturn in MW")

class ActualQuery(BaseModel):
    startDate: str = Field(..., description="Start date YYYY-MM-DD")
    endDate: str = Field(..., description="End date YYYY-MM-DD")
    resolution: str = Field("hourly_avg", description="'hourly_avg' or 'half_hourly'")
