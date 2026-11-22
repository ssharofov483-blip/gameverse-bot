import asyncio
import time
from typing import Optional, Any, Dict
from app.core.config import settings

try:
    import redis.asyncio as aioredis
except ImportError:
    aioredis = None


class InMemoryCache:
    def __init__(self):
        self._data: Dict[str, Any] = {}
        self._expiry: Dict[str, float] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[str]:
        async with self._lock:
            if key in self._expiry and time.time() > self._expiry[key]:
                del self._data[key]
                del self._expiry[key]
                return None
            val = self._data.get(key)
            return str(val) if val is not None else None

    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        async with self._lock:
            self._data[key] = str(value)
            if ex:
                self._expiry[key] = time.time() + ex
            elif key in self._expiry:
                del self._expiry[key]
            return True

    async def delete(self, key: str) -> bool:
        async with self._lock:
            self._data.pop(key, None)
            self._expiry.pop(key, None)
            return True


class CacheManager:
    def __init__(self):
        self._redis = None
        self._memory = InMemoryCache()

    async def connect(self):
        if settings.REDIS_ENABLED and aioredis:
            try:
                self._redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
                await self._redis.ping()
            except Exception:
                self._redis = None

    async def get(self, key: str) -> Optional[str]:
        if self._redis:
            try:
                return await self._redis.get(key)
            except Exception:
                pass
        return await self._memory.get(key)

    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        if self._redis:
            try:
                return await self._redis.set(key, value, ex=ex)
            except Exception:
                pass
        return await self._memory.set(key, value, ex=ex)

    async def delete(self, key: str) -> bool:
        if self._redis:
            try:
                return await self._redis.delete(key)
            except Exception:
                pass
        return await self._memory.delete(key)

    async def close(self):
        if self._redis:
            await self._redis.close()


cache = CacheManager()
