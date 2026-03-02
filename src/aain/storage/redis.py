from __future__ import annotations

from typing import Any

from aain.storage.base import BaseStore


class RedisStore(BaseStore):
    """Redis-backed persistent store.

    Requires: pip install aain[redis]

    Usage:
        store = RedisStore("redis://localhost:6379/0")
        await store.connect()
    """

    def __init__(self, url: str = "redis://localhost:6379/0"):
        self._url = url
        self._client: Any = None

    async def connect(self) -> None:
        try:
            import redis.asyncio as aioredis
            self._client = aioredis.from_url(self._url, decode_responses=True)
            await self._client.ping()
        except ImportError:
            raise ImportError(
                "Redis support requires the redis package. "
                "Install with: pip install aain[redis]"
            )

    async def disconnect(self) -> None:
        if self._client:
            await self._client.close()

    async def get(self, key: str) -> Any:
        if not self._client:
            raise RuntimeError("Not connected. Call connect() first.")
        import json
        raw = await self._client.get(key)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return raw

    async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        if not self._client:
            raise RuntimeError("Not connected. Call connect() first.")
        import json
        serialized = json.dumps(value) if not isinstance(value, str) else value
        if ttl_seconds:
            await self._client.setex(key, ttl_seconds, serialized)
        else:
            await self._client.set(key, serialized)

    async def delete(self, key: str) -> None:
        if not self._client:
            raise RuntimeError("Not connected. Call connect() first.")
        await self._client.delete(key)

    async def exists(self, key: str) -> bool:
        if not self._client:
            raise RuntimeError("Not connected. Call connect() first.")
        return bool(await self._client.exists(key))
