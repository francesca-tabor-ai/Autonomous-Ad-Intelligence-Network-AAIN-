from __future__ import annotations

import pytest

from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.event_bus import AsyncEventBus
from aain.core.types import EventType
from aain.clusters.placement.supervisor import PlacementClusterSupervisor
from aain.llm.mock import MockLLM
from aain.models.intent import IntentSignal, IntentType, UserState
from aain.models.placement import PlacementDecision, InsertionPoint


@pytest.fixture
def cluster() -> PlacementClusterSupervisor:
    return PlacementClusterSupervisor(AsyncEventBus(), MockLLM())


def _event(bb: Blackboard) -> Event:
    return Event(
        event_type=EventType.PIPELINE_STAGE,
        source_agent_id="test",
        correlation_id=bb.correlation_id,
        payload={"stage": "placement"},
    )


async def test_selects_surface_low_fatigue(cluster: PlacementClusterSupervisor) -> None:
    bb = Blackboard("test-1")
    bb.write("test", "user_state", UserState(session_id="s1", ad_fatigue_score=0.1))
    bb.write("test", "parsed_intent", IntentSignal(
        query="best CRM", intent_type=IntentType.COMMERCIAL_INVESTIGATION, confidence=0.8,
    ))

    await cluster.run_cluster(_event(bb), bb)

    decision: PlacementDecision = bb.read("placement_decision")
    assert decision is not None
    assert decision.surface.intrusiveness_level <= 4


async def test_reduces_intrusiveness_high_fatigue(cluster: PlacementClusterSupervisor) -> None:
    bb = Blackboard("test-2")
    bb.write("test", "user_state", UserState(session_id="s1", ad_fatigue_score=0.8))
    bb.write("test", "parsed_intent", IntentSignal(
        query="test", intent_type=IntentType.INFORMATIONAL, confidence=0.5,
    ))

    await cluster.run_cluster(_event(bb), bb)

    decision: PlacementDecision = bb.read("placement_decision")
    assert decision.surface.intrusiveness_level <= 1


async def test_conversational_insertion(cluster: PlacementClusterSupervisor) -> None:
    bb = Blackboard("test-3")
    bb.write("test", "user_state", UserState(session_id="s1", ad_fatigue_score=0.0))
    bb.write("test", "parsed_intent", IntentSignal(
        query="best CRM tools", intent_type=IntentType.COMMERCIAL_INVESTIGATION, confidence=0.8,
    ))

    await cluster.run_cluster(_event(bb), bb)

    insertion: InsertionPoint = bb.read("insertion_point")
    assert insertion is not None
    assert insertion.transition_text != ""


async def test_placement_creates_render_spec(cluster: PlacementClusterSupervisor) -> None:
    bb = Blackboard("test-4")
    bb.write("test", "user_state", UserState(session_id="s1"))
    bb.write("test", "parsed_intent", IntentSignal(
        query="test", intent_type=IntentType.INFORMATIONAL, confidence=0.5,
    ))

    await cluster.run_cluster(_event(bb), bb)

    decision: PlacementDecision = bb.read("placement_decision")
    assert decision.render_spec is not None
    assert decision.render_spec.format in ("native", "banner")
