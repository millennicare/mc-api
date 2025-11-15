import json
from typing import Any, Optional

from redis.asyncio import Redis

from src.core.config import cache_settings


class CacheClient:
    def __init__(self):
        self.redis = Redis(
            host=cache_settings.redis_host, port=cache_settings.redis_port, db=0
        )

    async def set(self, key: str, value: Any, expires: int = 600) -> None:
        """
        Store a value in Redis with expiration.

        Args:
            key: Cache key
            value: Value to store (will be JSON serialized if not string)
            expire: Expiration time in seconds (default: 600 = 10 minutes)
        """
        # Serialize value if it's not a string
        if not isinstance(value, str):
            value = json.dumps(value)

        await self.redis.set(key, value, ex=expires)

    async def get(self, key: str) -> Optional[str]:
        """
        Retrieve a value from Redis.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        value = await self.redis.get(key)

        if value is None:
            return None

        # Redis returns bytes, decode to string
        if isinstance(value, bytes):
            return value.decode("utf-8")

        return value

    async def delete(self, key: str) -> bool:
        """
        Delete a value from Redis.

        Args:
            key: Cache key

        Returns:
            True if key was found and deleted, False otherwise
        """
        result = await self.redis.delete(key)
        return result > 0

    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in Redis.

        Args:
            key: Cache key

        Returns:
            True if key exists, False otherwise
        """
        result = await self.redis.exists(key)
        return result > 0

    async def clear_pattern(self, pattern: str):
        """
        Clear all keys matching a pattern.

        Args:
            pattern: Redis key pattern (e.g., "oauth_state:*")
        """
        keys = await self.redis.keys(pattern)
        if keys:
            await self.redis.delete(*keys)
