from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Callable, Awaitable

from aain.core.events import Event
from aain.core.types import EventType
from aain.utils.logging import get_logger

log = get_logger("event_bus")

Subscriber = Callable[[Event], Awaitable[None]]

_WILDCARD = "ALL"


class AsyncEventBus:
    """In-process async pub/sub with topic filtering and ring-buffer history."""

    def __init__(self, max_history: int = 10_000, handler_timeout_s: float = 0.1):
        self._subscribers: dict[EventType | str, list[Subscriber]] = defaultdict(list)
        self._history: list[Event] = []
        self._max_history = max_history
        self._handler_timeout = handler_timeout_s

    async def publish(self, event: Event) -> None:
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        targets = list(self._subscribers.get(event.event_type, []))
        targets += list(self._subscribers.get(_WILDCARD, []))

        if targets:
            await asyncio.gather(
                *(self._safe_dispatch(sub, event) for sub in targets),
                return_exceptions=True,
            )

    def subscribe(self, event_type: EventType | str, callback: Subscriber) -> None:
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: EventType | str, callback: Subscriber) -> None:
        subs = self._subscribers.get(event_type, [])
        if callback in subs:
            subs.remove(callback)

    async def _safe_dispatch(self, subscriber: Subscriber, event: Event) -> None:
        try:
            await asyncio.wait_for(subscriber(event), timeout=self._handler_timeout)
        except asyncio.TimeoutError:
            log.warning("handler_timeout", event_type=event.event_type)
        except Exception as exc:
            log.error("handler_error", event_type=event.event_type, error=str(exc))

    def get_history(
        self, event_type: EventType | None = None, limit: int = 100
    ) -> list[Event]:
        if event_type:
            return [e for e in self._history if e.event_type == event_type][-limit:]
        return self._history[-limit:]

    def clear_history(self) -> None:
        self._history.clear()

    @property
    def subscriber_count(self) -> int:
        return sum(len(subs) for subs in self._subscribers.values())
