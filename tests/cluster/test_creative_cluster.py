from __future__ import annotations

import pytest

from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.event_bus import AsyncEventBus
from aain.core.types import EventType
from aain.clusters.creative.supervisor import CreativeClusterSupervisor
from aain.llm.mock import MockLLM
from aain.models.campaign import Campaign, Creative
from aain.models.intent import IntentSignal, IntentType
from aain.models.creative import CreativeVariant


@pytest.fixture
def cluster() -> CreativeClusterSupervisor:
    return CreativeClusterSupervisor(AsyncEventBus(), MockLLM())


def _event(bb: Blackboard) -> Event:
    return Event(
        event_type=EventType.PIPELINE_STAGE,
        source_agent_id="test",
        correlation_id=bb.correlation_id,
        payload={"stage": "creative"},
    )


def _setup(bb: Blackboard) -> None:
    campaign = Campaign(
        campaign_id="camp_001", advertiser_id="adv_1", name="Test CRM",
        budget_total=1000, budget_remaining=800,
        targeting_categories=["saas", "crm"],
        creatives=[
            Creative(creative_id="cr1", headline="Best CRM Ever",
                     body="Try it today.", cta_text="Start Free Trial"),
        ],
    )
    bb.write("test", "winning_campaign", campaign)
    bb.write("test", "candidate_campaigns", [campaign])
    bb.write("test", "parsed_intent", IntentSignal(
        query="best CRM for startups",
        intent_type=IntentType.COMMERCIAL_INVESTIGATION,
        confidence=0.8, categories=["saas"],
    ))


async def test_generates_creative(cluster: CreativeClusterSupervisor) -> None:
    bb = Blackboard("test-1")
    _setup(bb)

    await cluster.run_cluster(_event(bb), bb)

    creative: CreativeVariant = bb.read("generated_creative")
    assert creative is not None
    assert creative.headline != ""
    assert creative.campaign_id == "camp_001"


async def test_assigns_variant_group(cluster: CreativeClusterSupervisor) -> None:
    bb = Blackboard("test-2")
    _setup(bb)

    await cluster.run_cluster(_event(bb), bb)

    final: CreativeVariant = bb.read("final_creative")
    assert final is not None
    assert final.test_group in ("control", "variant_a", "variant_b")


async def test_selects_assets(cluster: CreativeClusterSupervisor) -> None:
    bb = Blackboard("test-3")
    _setup(bb)

    await cluster.run_cluster(_event(bb), bb)

    assets = bb.read("selected_assets")
    assert assets is not None
    assert len(assets) > 0


async def test_personalization_signals(cluster: CreativeClusterSupervisor) -> None:
    bb = Blackboard("test-4")
    _setup(bb)

    await cluster.run_cluster(_event(bb), bb)

    creative: CreativeVariant = bb.read("generated_creative")
    assert "query" in creative.personalization_signals
    assert "intent_type" in creative.personalization_signals


async def test_no_campaign_no_creative(cluster: CreativeClusterSupervisor) -> None:
    bb = Blackboard("test-5")
    bb.write("test", "candidate_campaigns", [])
    bb.write("test", "parsed_intent", IntentSignal(
        query="test", intent_type=IntentType.INFORMATIONAL, confidence=0.5,
    ))

    await cluster.run_cluster(_event(bb), bb)

    creative = bb.read("generated_creative")
    assert creative is None
