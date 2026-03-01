from __future__ import annotations

import asyncio
import pytest

from aain.core.events import Event
from aain.core.event_bus import AsyncEventBus
from aain.core.types import EventType


@pytest.fixture
def bus() -> AsyncEventBus:
    return AsyncEventBus(max_history=100)


async def test_publish_subscribe(bus: AsyncEventBus) -> None:
    received: list[Event] = []

    async def handler(event: Event) -> None:
        received.append(event)

    bus.subscribe(EventType.INTENT, handler)

    event = Event(
        event_type=EventType.INTENT,
        source_agent_id="test",
        payload={"query": "test query"},
    )
    await bus.publish(event)

    assert len(received) == 1
    assert received[0].payload["query"] == "test query"


async def test_wildcard_subscription(bus: AsyncEventBus) -> None:
    received: list[Event] = []

    async def handler(event: Event) -> None:
        received.append(event)

    bus.subscribe("ALL", handler)

    await bus.publish(Event(event_type=EventType.INTENT, source_agent_id="test"))
    await bus.publish(Event(event_type=EventType.AUCTION, source_agent_id="test"))

    assert len(received) == 2


async def test_handler_timeout(bus: AsyncEventBus) -> None:
    async def slow_handler(event: Event) -> None:
        await asyncio.sleep(1.0)

    bus.subscribe(EventType.INTENT, slow_handler)
    # Should not raise — timeout is handled internally
    await bus.publish(Event(event_type=EventType.INTENT, source_agent_id="test"))


async def test_handler_error_isolation(bus: AsyncEventBus) -> None:
    received: list[Event] = []

    async def bad_handler(event: Event) -> None:
        raise ValueError("boom")

    async def good_handler(event: Event) -> None:
        received.append(event)

    bus.subscribe(EventType.INTENT, bad_handler)
    bus.subscribe(EventType.INTENT, good_handler)

    await bus.publish(Event(event_type=EventType.INTENT, source_agent_id="test"))
    assert len(received) == 1


async def test_history(bus: AsyncEventBus) -> None:
    for i in range(5):
        await bus.publish(Event(
            event_type=EventType.INTENT, source_agent_id="test", payload={"i": i}
        ))

    history = bus.get_history(limit=3)
    assert len(history) == 3

    intent_history = bus.get_history(event_type=EventType.INTENT)
    assert len(intent_history) == 5


async def test_unsubscribe(bus: AsyncEventBus) -> None:
    received: list[Event] = []

    async def handler(event: Event) -> None:
        received.append(event)

    bus.subscribe(EventType.INTENT, handler)
    await bus.publish(Event(event_type=EventType.INTENT, source_agent_id="test"))
    assert len(received) == 1

    bus.unsubscribe(EventType.INTENT, handler)
    await bus.publish(Event(event_type=EventType.INTENT, source_agent_id="test"))
    assert len(received) == 1
