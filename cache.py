import hashlib
import json
import redis.asyncio as redis
from config import Config

class Cache:
    def __init__(self):
        self.redis = None
        if Config.ENABLE_CACHE:
            try:
                self.redis = redis.from_url(Config.REDIS_URL, encoding="utf-8", decode_responses=True)
            except Exception as e:
                print(f"Failed to connect to Redis: {e}")

    def _generate_key(self, request_data: dict) -> str:
        # Create a unique key based on the request content
        # We sort keys to ensure consistent ordering
        serialized = json.dumps(request_data, sort_keys=True)
        return hashlib.sha256(serialized.encode()).hexdigest()

    async def get(self, request_data: dict) -> dict:
        if not self.redis:
            return None
        
        key = self._generate_key(request_data)
        try:
            cached_data = await self.redis.get(key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            print(f"Cache get error: {e}")
        return None

    async def set(self, request_data: dict, response_data: dict, expire: int = 3600):
        if not self.redis:
            return

        key = self._generate_key(request_data)
        try:
            await self.redis.set(key, json.dumps(response_data), ex=expire)
        except Exception as e:
            print(f"Cache set error: {e}")

# Global cache instance
cache = Cache()
