from pydantic import BaseModel, Field
from typing import List, Dict, Any

class CutoffOption(BaseModel):
    time: str = Field(..., description="Time string HH:MM")
    label: str = Field(..., description="Human-readable label with market justification")
    description: str = Field(..., description="Energy market context")

class DatasetInfo(BaseModel):
    name: str
    endpoint: str
    description: str
    documentedUnits: str
    fields: List[str]

class MetadataResponse(BaseModel):
    projectName: str
    version: str
    timezone: str
    datasets: List[DatasetInfo]
    supportedDateRangeMin: str
    supportedDateRangeMax: str
    defaultDateRangeStart: str
    defaultDateRangeEnd: str
    defaultCutoff: str
    availableCutoffs: List[CutoffOption]
    dataFreshnessStatus: str
    lastRefreshUtc: str
    isDemoData: bool
    dataLimitationsNotice: str
