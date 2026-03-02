from __future__ import annotations

import pytest

from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.event_bus import AsyncEventBus
from aain.core.types import EventType
from aain.clusters.economic.supervisor import EconomicClusterSupervisor
from aain.models.auction import AuctionResult, Bid
from aain.models.campaign import Campaign, Creative
from aain.models.intent import IntentSignal, IntentType, UserState, CommercialRelevance


@pytest.fixture
def cluster() -> EconomicClusterSupervisor:
    return EconomicClusterSupervisor(AsyncEventBus())


def _event(bb: Blackboard) -> Event:
    return Event(
        event_type=EventType.PIPELINE_STAGE,
        source_agent_id="test",
        correlation_id=bb.correlation_id,
        payload={"stage": "economic"},
    )


def _setup_bids(bb: Blackboard) -> None:
    campaigns = [
        Campaign(campaign_id="c1", advertiser_id="a1", name="C1",
                 budget_total=1000, budget_remaining=800, base_bid=3.0),
        Campaign(campaign_id="c2", advertiser_id="a2", name="C2",
                 budget_total=500, budget_remaining=400, base_bid=2.0),
    ]
    bids = [
        Bid(campaign_id="c1", advertiser_id="a1", bid_amount=3.0,
            relevance_score=0.8, quality_score=0.9),
        Bid(campaign_id="c2", advertiser_id="a2", bid_amount=2.0,
            relevance_score=0.6, quality_score=0.7),
    ]
    bb.write("test", "candidate_campaigns", campaigns)
    bb.write("test", "bids", bids)
    bb.write("test", "commercial_relevance", CommercialRelevance(score=0.8, category="saas"))
    bb.write("test", "user_state", UserState(session_id="s1", engagement_level=0.6))
    bb.write("test", "parsed_intent", IntentSignal(
        query="best CRM", intent_type=IntentType.COMMERCIAL_INVESTIGATION, confidence=0.8,
    ))


async def test_runs_second_price_auction(cluster: EconomicClusterSupervisor) -> None:
    bb = Blackboard("test-1")
    _setup_bids(bb)

    await cluster.run_cluster(_event(bb), bb)

    result: AuctionResult = bb.read("auction_result")
    assert result is not None
    assert result.winner_campaign_id == "c1"
    assert result.clearing_price < result.winning_bid
    assert result.participants == 2


async def test_sets_winning_campaign(cluster: EconomicClusterSupervisor) -> None:
    bb = Blackboard("test-2")
    _setup_bids(bb)

    await cluster.run_cluster(_event(bb), bb)

    winner: Campaign = bb.read("winning_campaign")
    assert winner is not None
    assert winner.campaign_id == "c1"


async def test_final_price_set(cluster: EconomicClusterSupervisor) -> None:
    bb = Blackboard("test-3")
    _setup_bids(bb)

    await cluster.run_cluster(_event(bb), bb)

    price = bb.read("final_price")
    assert price is not None
    assert price > 0


async def test_ltv_prediction(cluster: EconomicClusterSupervisor) -> None:
    bb = Blackboard("test-4")
    _setup_bids(bb)
    bb.write("test", "user_state", UserState(
        session_id="s1", engagement_level=0.9,
        conversion_probability=0.5, session_queries=["q1", "q2", "q3"],
    ))

    await cluster.run_cluster(_event(bb), bb)

    ltv = bb.read("user_ltv_estimate")
    tier = bb.read("ltv_tier")
    assert ltv is not None
    assert tier in ("low", "medium", "high")


async def test_no_bids_no_auction(cluster: EconomicClusterSupervisor) -> None:
    bb = Blackboard("test-5")
    bb.write("test", "bids", [])
    bb.write("test", "candidate_campaigns", [])
    bb.write("test", "commercial_relevance", CommercialRelevance(score=0.3))
    bb.write("test", "user_state", UserState(session_id="s1"))

    await cluster.run_cluster(_event(bb), bb)

    result = bb.read("auction_result")
    assert result is None
