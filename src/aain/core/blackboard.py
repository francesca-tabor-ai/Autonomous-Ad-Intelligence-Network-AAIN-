from __future__ import annotations

from typing import Any


class Blackboard:
    """Shared context for a single pipeline execution.

    Agents read/write to the blackboard during their pipeline stage.
    Safe under asyncio (single-threaded event loop).
    """

    def __init__(self, correlation_id: str):
        self.correlation_id = correlation_id
        self._data: dict[str, Any] = {}
        self._write_log: list[tuple[str, str, Any]] = []

    def write(self, agent_id: str, key: str, value: Any) -> None:
        self._data[key] = value
        self._write_log.append((agent_id, key, value))

    def read(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def has(self, key: str) -> bool:
        return key in self._data

    def snapshot(self) -> dict[str, Any]:
        return dict(self._data)

    @property
    def audit_trail(self) -> list[tuple[str, str, Any]]:
        return list(self._write_log)
