import os
import json
import time
from typing import Optional, Any
from app.core.config import settings
from app.core.logging import logger

class CacheService:
    def __init__(self, cache_dir: str = settings.CACHE_DIR, default_ttl: int = settings.CACHE_TTL_SECONDS):
        self.cache_dir = cache_dir
        self.default_ttl = default_ttl
        self.memory_cache = {}
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def _get_file_path(self, key: str) -> str:
        safe_key = "".join([c if c.isalnum() or c in "-_" else "_" for c in key])
        return os.path.join(self.cache_dir, f"{safe_key}.json")
        
    def get(self, key: str) -> Optional[Any]:
        now = time.time()
        # 1. Check memory cache
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if entry["expiry"] > now:
                return entry["data"]
            else:
                del self.memory_cache[key]
                
        # 2. Check disk cache
        file_path = self._get_file_path(key)
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    entry = json.load(f)
                if entry.get("expiry", 0) > now:
                    self.memory_cache[key] = entry
                    return entry.get("data")
                else:
                    os.remove(file_path)
            except Exception as e:
                logger.warning(f"Error reading disk cache for {key}: {e}")
                
        return None
        
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> None:
        if ttl is None:
            ttl = self.default_ttl
        now = time.time()
        entry = {
            "expiry": now + ttl,
            "created_at": now,
            "data": data
        }
        self.memory_cache[key] = entry
        
        file_path = self._get_file_path(key)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(entry, f)
        except Exception as e:
            logger.warning(f"Error saving to disk cache for {key}: {e}")

    def clear(self) -> None:
        self.memory_cache.clear()
        for fname in os.listdir(self.cache_dir):
            if fname.endswith(".json"):
                try:
                    os.remove(os.path.join(self.cache_dir, fname))
                except Exception:
                    pass

cache_service = CacheService()
