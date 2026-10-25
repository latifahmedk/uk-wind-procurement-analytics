from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "UK Wind Power Forecast & Day-Ahead Procurement Analytics"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api"
    
    # Elexon Insights Solution (BMRS API)
    ELEXON_BASE_URL: str = "https://data.elexon.co.uk/bmrs/api/v1"
    
    # Procurement default cutoff time (Europe/London time, D-1)
    # 11:00 corresponds to standard UK Day-Ahead power auction gate closure (EPEX SPOT / Nord Pool)
    DEFAULT_DECISION_CUTOFF: str = "11:00"
    
    # Timezone
    TIMEZONE: str = "Europe/London"
    
    # Cache settings
    CACHE_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data_cache")
    CACHE_TTL_SECONDS: int = 3600
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]
    
    # Demo data fallback flag
    ALLOW_DEMO_FALLBACK: bool = True
    
    # Networking
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()
