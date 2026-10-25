from fastapi import APIRouter
from datetime import datetime
from app.services.elexon_client import elexon_client
from app.core.config import settings

router = APIRouter(tags=["Health"])

@router.get("/health")
async def get_health():
    """Health check endpoint indicating service and upstream API connectivity."""
    upstream_status = await elexon_client.check_health()
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "timestampUtc": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "upstreamElexonApi": upstream_status
    }
