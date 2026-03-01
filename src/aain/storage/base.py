from __future__ import annotations

import abc
from typing import Any


class BaseStore(abc.ABC):
    @abc.abstractmethod
    async def get(self, key: str) -> Any:
        ...

    @abc.abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        ...

    @abc.abstractmethod
    async def delete(self, key: str) -> None:
        ...

    @abc.abstractmethod
    async def exists(self, key: str) -> bool:
        ...
