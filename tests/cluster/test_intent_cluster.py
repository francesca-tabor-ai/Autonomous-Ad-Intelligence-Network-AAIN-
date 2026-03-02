from __future__ import annotations

import pytest

from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.event_bus import AsyncEventBus
from aain.core.types import EventType
from aain.clusters.intent.supervisor import IntentClusterSupervisor
from aain.llm.mock import MockLLM
from aain.models.intent import IntentSignal, IntentType, CommercialRelevance, UserState


@pytest.fixture
def cluster() -> IntentClusterSupervisor:
    bus = AsyncEventBus()
    return IntentClusterSupervisor(bus, MockLLM())


def _make_event(bb: Blackboard, stage: str = "intent") -> Event:
    return Event(
        event_type=EventType.PIPELINE_STAGE,
        source_agent_id="test",
        correlation_id=bb.correlation_id,
        payload={"stage": stage},
    )


async def test_parses_commercial_intent(cluster: IntentClusterSupervisor) -> None:
    bb = Blackboard("test-1")
    bb.write("pipeline", "trigger_payload", {
        "query": "What's the best CRM for startups?",
        "session_id": "s1", "user_id": "u1",
    })

    await cluster.run_cluster(_make_event(bb), bb)

    intent: IntentSignal = bb.read("parsed_intent")
    assert intent is not None
    assert intent.intent_type == IntentType.COMMERCIAL_INVESTIGATION
    assert intent.confidence >= 0.7
    assert "saas" in intent.categories


async def test_parses_transactional_intent(cluster: IntentClusterSupervisor) -> None:
    bb = Blackboard("test-2")
    bb.write("pipeline", "trigger_payload", {
        "query": "buy CRM software subscribe now",
        "session_id": "s1", "user_id": "u1",
    })

    await cluster.run_cluster(_make_event(bb), bb)

    intent: IntentSignal = bb.read("parsed_intent")
    assert intent.intent_type == IntentType.TRANSACTIONAL


async def test_commercial_relevance_score(cluster: IntentClusterSupervisor) -> None:
    bb = Blackboard("test-3")
    bb.write("pipeline", "trigger_payload", {
        "query": "compare top CRM tools pricing",
        "session_id": "s1", "user_id": "u1",
    })

    await cluster.run_cluster(_make_event(bb), bb)

    relevance: CommercialRelevance = bb.read("commercial_relevance")
    assert relevance is not None
    assert relevance.score >= 0.5
    assert relevance.is_eligible is True


async def test_low_commercial_relevance_for_informational(cluster: IntentClusterSupervisor) -> None:
    bb = Blackboard("test-4")
    bb.write("pipeline", "trigger_payload", {
        "query": "how does photosynthesis work",
        "session_id": "s1", "user_id": "u1",
    })

    await cluster.run_cluster(_make_event(bb), bb)

    relevance: CommercialRelevance = bb.read("commercial_relevance")
    assert relevance.score < 0.5


async def test_user_state_tracking(cluster: IntentClusterSupervisor) -> None:
    bb = Blackboard("test-5")
    bb.write("pipeline", "trigger_payload", {
        "query": "best CRM", "session_id": "session_abc", "user_id": "user_1",
    })

    await cluster.run_cluster(_make_event(bb), bb)

    state: UserState = bb.read("user_state")
    assert state is not None
    assert state.session_id == "session_abc"
    assert state.ads_shown_count == 0
    assert state.ad_fatigue_score == 0.0


async def test_ignores_wrong_stage(cluster: IntentClusterSupervisor) -> None:
    bb = Blackboard("test-6")
    bb.write("pipeline", "trigger_payload", {"query": "test", "session_id": "s1"})
    event = Event(
        event_type=EventType.PIPELINE_STAGE,
        source_agent_id="test",
        correlation_id=bb.correlation_id,
        payload={"stage": "advertiser"},
    )

    result = await cluster.process(event, bb)
    assert result is None
