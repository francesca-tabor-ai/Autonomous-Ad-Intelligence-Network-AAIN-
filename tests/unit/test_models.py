from __future__ import annotations

import pytest
from pydantic import ValidationError

from aain.models.intent import IntentSignal, IntentType, CommercialRelevance, UserState
from aain.models.auction import Bid, AuctionResult
from aain.models.campaign import Campaign, Creative
from aain.models.reward import GlobalReward


def test_intent_signal() -> None:
    signal = IntentSignal(
        query="best crm for startups",
        intent_type=IntentType.COMMERCIAL_INVESTIGATION,
        confidence=0.85,
        entities=["CRM"],
        categories=["saas"],
    )
    assert signal.confidence == 0.85
    assert signal.intent_type == IntentType.COMMERCIAL_INVESTIGATION


def test_intent_signal_validation() -> None:
    with pytest.raises(ValidationError):
        IntentSignal(
            query="test", intent_type=IntentType.INFORMATIONAL, confidence=1.5
        )


def test_commercial_relevance() -> None:
    cr = CommercialRelevance(score=0.82, category="saas", is_eligible=True)
    assert cr.score == 0.82


def test_user_state() -> None:
    state = UserState(session_id="s1", engagement_level=0.6, ad_fatigue_score=0.3)
    assert state.ads_shown_count == 0


def test_bid() -> None:
    bid = Bid(
        campaign_id="c1", advertiser_id="a1",
        bid_amount=2.50, relevance_score=0.8,
    )
    assert bid.bid_amount == 2.50


def test_auction_result() -> None:
    result = AuctionResult(
        winner_campaign_id="c1",
        winning_bid=5.0,
        clearing_price=3.5,
        participants=3,
    )
    assert result.clearing_price == 3.5


def test_campaign() -> None:
    c = Campaign(
        campaign_id="c1", advertiser_id="a1",
        name="Test Campaign", budget_total=1000.0, budget_remaining=750.0,
    )
    assert c.budget_remaining == 750.0


def test_global_reward() -> None:
    r = GlobalReward(total=0.65, revenue_component=3.0, engagement_component=0.7)
    assert "alpha" in r.weights


def test_model_serialization_roundtrip() -> None:
    signal = IntentSignal(
        query="test", intent_type=IntentType.TRANSACTIONAL, confidence=0.9,
    )
    data = signal.model_dump()
    restored = IntentSignal.model_validate(data)
    assert restored.query == signal.query
    assert restored.confidence == signal.confidence
