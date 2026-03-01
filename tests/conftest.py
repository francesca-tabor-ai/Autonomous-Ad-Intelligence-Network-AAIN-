from __future__ import annotations

import pytest

from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.event_bus import AsyncEventBus
from aain.core.types import EventType
from aain.llm.mock import MockLLM
from aain.utils.ids import generate_correlation_id


@pytest.fixture
def event_bus() -> AsyncEventBus:
    return AsyncEventBus(max_history=1000)


@pytest.fixture
def mock_llm() -> MockLLM:
    return MockLLM()


@pytest.fixture
def correlation_id() -> str:
    return generate_correlation_id()


@pytest.fixture
def blackboard(correlation_id: str) -> Blackboard:
    return Blackboard(correlation_id)


def make_event(
    event_type: EventType = EventType.PIPELINE_STAGE,
    source: str = "test",
    correlation_id: str = "",
    payload: dict | None = None,
) -> Event:
    return Event(
        event_type=event_type,
        source_agent_id=source,
        correlation_id=correlation_id or generate_correlation_id(),
        payload=payload or {},
    )


def make_intent_trigger(query: str = "What's the best CRM for startups?") -> dict:
    return {
        "query": query,
        "session_id": "test_session",
        "user_id": "test_user",
    }
