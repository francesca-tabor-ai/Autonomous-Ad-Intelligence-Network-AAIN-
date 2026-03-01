from __future__ import annotations

import time
from typing import Any

from aain.storage.base import BaseStore


class InMemoryStore(BaseStore):
    def __init__(self) -> None:
        self._data: dict[str, tuple[Any, float | None]] = {}

    async def get(self, key: str) -> Any:
        entry = self._data.get(key)
        if entry is None:
            return None
        value, expires = entry
        if expires and time.time() > expires:
            del self._data[key]
            return None
        return value

    async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        expires = time.time() + ttl_seconds if ttl_seconds else None
        self._data[key] = (value, expires)

    async def delete(self, key: str) -> None:
        self._data.pop(key, None)

    async def exists(self, key: str) -> bool:
        return await self.get(key) is not None
