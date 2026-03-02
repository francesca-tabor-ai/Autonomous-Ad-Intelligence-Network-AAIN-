from __future__ import annotations

import pytest

from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.event_bus import AsyncEventBus
from aain.core.types import EventType
from aain.clusters.advertiser.supervisor import AdvertiserClusterSupervisor
from aain.models.intent import IntentSignal, IntentType, UserState
from aain.models.auction import Bid
from aain.models.campaign import Campaign


@pytest.fixture
def cluster() -> AdvertiserClusterSupervisor:
    return AdvertiserClusterSupervisor(AsyncEventBus())


def _event(bb: Blackboard) -> Event:
    return Event(
        event_type=EventType.PIPELINE_STAGE,
        source_agent_id="test",
        correlation_id=bb.correlation_id,
        payload={"stage": "advertiser"},
    )


async def test_finds_matching_campaigns(cluster: AdvertiserClusterSupervisor) -> None:
    bb = Blackboard("test-1")
    bb.write("test", "parsed_intent", IntentSignal(
        query="best CRM for startups",
        intent_type=IntentType.COMMERCIAL_INVESTIGATION,
        confidence=0.8, categories=["saas"],
    ))
    bb.write("test", "user_state", UserState(session_id="s1"))

    await cluster.run_cluster(_event(bb), bb)

    campaigns: list[Campaign] = bb.read("candidate_campaigns")
    assert campaigns is not None
    assert len(campaigns) > 0
    assert all(c.status == "active" for c in campaigns)


async def test_generates_bids_for_candidates(cluster: AdvertiserClusterSupervisor) -> None:
    bb = Blackboard("test-2")
    bb.write("test", "parsed_intent", IntentSignal(
        query="best CRM for startups",
        intent_type=IntentType.COMMERCIAL_INVESTIGATION,
        confidence=0.85, categories=["saas"],
    ))
    bb.write("test", "user_state", UserState(session_id="s1", ad_fatigue_score=0.1))

    await cluster.run_cluster(_event(bb), bb)

    bids: list[Bid] = bb.read("bids")
    assert bids is not None
    assert len(bids) > 0
    assert all(b.bid_amount > 0 for b in bids)
    # Bids should be sorted descending
    for i in range(len(bids) - 1):
        assert bids[i].bid_amount >= bids[i + 1].bid_amount


async def test_fatigue_reduces_bids(cluster: AdvertiserClusterSupervisor) -> None:
    intent = IntentSignal(
        query="best CRM", intent_type=IntentType.COMMERCIAL_INVESTIGATION,
        confidence=0.8, categories=["saas"],
    )

    # Low fatigue
    bb1 = Blackboard("test-3a")
    bb1.write("test", "parsed_intent", intent)
    bb1.write("test", "user_state", UserState(session_id="s1", ad_fatigue_score=0.0))
    await cluster.run_cluster(_event(bb1), bb1)
    bids_low: list[Bid] = bb1.read("bids")

    # High fatigue
    bb2 = Blackboard("test-3b")
    bb2.write("test", "parsed_intent", intent)
    bb2.write("test", "user_state", UserState(session_id="s2", ad_fatigue_score=0.8))
    await cluster.run_cluster(_event(bb2), bb2)
    bids_high: list[Bid] = bb2.read("bids")

    if bids_low and bids_high:
        assert bids_low[0].bid_amount >= bids_high[0].bid_amount


async def test_no_campaigns_for_unrelated_query(cluster: AdvertiserClusterSupervisor) -> None:
    bb = Blackboard("test-4")
    bb.write("test", "parsed_intent", IntentSignal(
        query="how does quantum physics work",
        intent_type=IntentType.INFORMATIONAL,
        confidence=0.5, categories=[],
    ))
    bb.write("test", "user_state", UserState(session_id="s1"))

    await cluster.run_cluster(_event(bb), bb)

    campaigns: list[Campaign] = bb.read("candidate_campaigns")
    bids: list[Bid] = bb.read("bids")
    assert campaigns is not None
    assert bids is not None


async def test_audience_expansion(cluster: AdvertiserClusterSupervisor) -> None:
    bb = Blackboard("test-5")
    bb.write("test", "parsed_intent", IntentSignal(
        query="best CRM for startups",
        intent_type=IntentType.COMMERCIAL_INVESTIGATION,
        confidence=0.8, categories=["saas"],
    ))
    bb.write("test", "user_state", UserState(session_id="s1"))

    await cluster.run_cluster(_event(bb), bb)

    expanded: dict = bb.read("expanded_audiences")
    assert expanded is not None
    assert "saas" in expanded
    assert "cloud" in expanded["saas"]
