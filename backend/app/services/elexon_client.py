import httpx
import asyncio
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Tuple
import json
from app.core.config import settings
from app.core.logging import logger
from app.services.cache_service import cache_service
from app.services.demo_data_generator import generate_synthetic_fuelhh, generate_synthetic_windfor

class ElexonClient:
    def __init__(self, base_url: str = settings.ELEXON_BASE_URL):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Accept": "application/json",
            "User-Agent": "UKWindProcurementAnalytics/1.0 (Energy Analytics Pilot)"
        }
        self.timeout = httpx.Timeout(25.0, connect=10.0)
        
    async def check_health(self) -> Dict[str, Any]:
        """Verify upstream Elexon API responsiveness."""
        test_url = f"{self.base_url}/datasets/FUELHH/stream?settlementDateFrom=2026-01-01&settlementDateTo=2026-01-01&fuelType=WIND"
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=5.0) as client:
                resp = await client.get(test_url)
                if resp.status_code == 200:
                    return {"status": "UPSTREAM_ONLINE", "code": 200, "message": "Elexon BMRS API reachable"}
                return {"status": "UPSTREAM_DEGRADED", "code": resp.status_code, "message": resp.text[:100]}
        except Exception as e:
            return {"status": "UPSTREAM_OFFLINE", "code": 503, "error": str(e)}

    async def fetch_fuelhh_chunk(self, client: httpx.AsyncClient, chunk_start: str, chunk_end: str) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/datasets/FUELHH/stream"
        params = {
            "settlementDateFrom": chunk_start,
            "settlementDateTo": chunk_end,
            "fuelType": "WIND"
        }
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "data" in data:
            return data["data"]
        return []

    async def fetch_fuelhh(self, start_date: date, end_date: date) -> Tuple[List[Dict[str, Any]], bool]:
        """
        Fetch FUELHH wind actuals between start_date and end_date.
        Returns (records, is_demo).
        """
        cache_key = f"FUELHH_WIND_{start_date.isoformat()}_{end_date.isoformat()}"
        cached = cache_service.get(cache_key)
        if cached:
            return cached.get("records", []), cached.get("is_demo", False)
            
        all_records = []
        is_demo = False
        
        try:
            # Chunk by 7-day intervals for stability
            chunks = []
            curr = start_date
            while curr <= end_date:
                next_date = min(curr + timedelta(days=6), end_date)
                chunks.append((curr.strftime("%Y-%m-%d"), next_date.strftime("%Y-%m-%d")))
                curr = next_date + timedelta(days=1)
                
            async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
                for c_start, c_end in chunks:
                    chunk_records = await self.fetch_fuelhh_chunk(client, c_start, c_end)
                    all_records.extend(chunk_records)
                    
            logger.info(f"Fetched {len(all_records)} real FUELHH records from Elexon ({start_date} to {end_date})")
        except Exception as e:
            logger.error(f"Failed to fetch FUELHH from Elexon API: {e}")
            if settings.ALLOW_DEMO_FALLBACK:
                logger.warning("Falling back to synthetic demo data for FUELHH")
                all_records = generate_synthetic_fuelhh(start_date, end_date)
                is_demo = True
            else:
                raise RuntimeError(f"Elexon FUELHH fetch failed: {e}")
                
        # Cache results
        cache_service.set(cache_key, {"records": all_records, "is_demo": is_demo})
        return all_records, is_demo

    async def fetch_windfor_chunk(self, client: httpx.AsyncClient, pub_from_iso: str, pub_to_iso: str) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/datasets/WINDFOR/stream"
        params = {
            "publishDateTimeFrom": pub_from_iso,
            "publishDateTimeTo": pub_to_iso
        }
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "data" in data:
            return data["data"]
        return []

    async def fetch_windfor(self, pub_from: datetime, pub_to: datetime) -> Tuple[List[Dict[str, Any]], bool]:
        """
        Fetch WINDFOR wind forecasts published between pub_from and pub_to.
        Returns (records, is_demo).
        """
        cache_key = f"WINDFOR_{pub_from.isoformat()}_{pub_to.isoformat()}"
        cached = cache_service.get(cache_key)
        if cached:
            return cached.get("records", []), cached.get("is_demo", False)
            
        all_records = []
        is_demo = False
        
        try:
            # Chunk by 4-day intervals for WINDFOR because payloads have multiple snapshots
            chunks = []
            curr = pub_from
            while curr < pub_to:
                next_time = min(curr + timedelta(days=4), pub_to)
                chunks.append((
                    curr.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    next_time.strftime("%Y-%m-%dT%H:%M:%SZ")
                ))
                curr = next_time
                
            async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
                for c_start, c_end in chunks:
                    chunk_records = await self.fetch_windfor_chunk(client, c_start, c_end)
                    all_records.extend(chunk_records)
                    
            logger.info(f"Fetched {len(all_records)} real WINDFOR records from Elexon ({pub_from} to {pub_to})")
        except Exception as e:
            logger.error(f"Failed to fetch WINDFOR from Elexon API: {e}")
            if settings.ALLOW_DEMO_FALLBACK:
                logger.warning("Falling back to synthetic demo data for WINDFOR")
                all_records = generate_synthetic_windfor(pub_from.date(), pub_to.date())
                is_demo = True
            else:
                raise RuntimeError(f"Elexon WINDFOR fetch failed: {e}")
                
        cache_service.set(cache_key, {"records": all_records, "is_demo": is_demo})
        return all_records, is_demo

elexon_client = ElexonClient()
