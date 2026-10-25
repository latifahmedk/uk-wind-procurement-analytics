from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ForecastRecord(BaseModel):
    startTime: str = Field(..., description="Target delivery interval start time (ISO 8601 UTC)")
    publishTime: str = Field(..., description="When the forecast was published (ISO 8601 UTC)")
    generation: float = Field(..., description="Forecast wind generation in MW")

class SelectedForecastRecord(BaseModel):
    startTime: str = Field(..., description="Target delivery interval start time (ISO 8601 UTC)")
    startTimeLocal: str = Field(..., description="Target delivery interval start time in UK local time")
    publishTime: str = Field(..., description="Selected forecast publication time (ISO 8601 UTC)")
    publishTimeLocal: str = Field(..., description="Selected forecast publication time in UK local time")
    generationForecast: float = Field(..., description="Selected forecast wind generation in MW")
    cutoffTimeUtc: str = Field(..., description="The applicable decision cutoff applied (ISO 8601 UTC)")
    cutoffTimeLocal: str = Field(..., description="The applicable decision cutoff applied in UK local time")
    leadTimeHours: float = Field(..., description="Hours between forecast publication and delivery start")
    isEligible: bool = Field(True, description="True if published on or before decision cutoff")

class ForecastQuery(BaseModel):
    startDate: str = Field(..., description="Start date YYYY-MM-DD")
    endDate: str = Field(..., description="End date YYYY-MM-DD")
    filterBy: str = Field("delivery_date", description="'delivery_date' or 'decision_date'")
    decisionCutoff: str = Field("11:00", description="Cutoff time in UK local time HH:MM (e.g. 11:00)")
