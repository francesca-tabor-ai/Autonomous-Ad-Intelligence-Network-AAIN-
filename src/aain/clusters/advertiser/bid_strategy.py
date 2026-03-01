from __future__ import annotations

from typing import Any

from aain.core.agent import BaseAgent
from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.types import EventType
from aain.models.auction import Bid
from aain.models.campaign import Campaign
from aain.models.intent import IntentSignal, UserState


class BidStrategyAgent(BaseAgent):
    """Computes real-time optimal bids using predicted LTV and auction aggressiveness."""

    @property
    def subscriptions(self) -> list[EventType]:
        return [EventType.PIPELINE_STAGE]

    async def process(self, event: Event, blackboard: Blackboard) -> Any:
        campaigns: list[Campaign] = blackboard.read("candidate_campaigns", [])
        user_state: UserState | None = blackboard.read("user_state")
        intent: IntentSignal | None = blackboard.read("parsed_intent")

        if not campaigns:
            blackboard.write(self.agent_id, "bids", [])
            return []

        fatigue_factor = user_state.ad_fatigue_score if user_state else 0.0
        intent_confidence = intent.confidence if intent else 0.5

        bids: list[Bid] = []
        for campaign in campaigns:
            relevance = intent_confidence * 0.7 + 0.3
            bid_amount = campaign.base_bid * relevance * (1.0 - fatigue_factor * 0.5)
            bid_amount = max(campaign.bid_floor, min(campaign.bid_ceiling, bid_amount))

            bids.append(Bid(
                campaign_id=campaign.campaign_id,
                advertiser_id=campaign.advertiser_id,
                bid_amount=round(bid_amount, 4),
                bid_type=campaign.pricing_model,
                relevance_score=round(relevance, 2),
                quality_score=round(min(1.0, relevance * 0.8 + 0.2), 2),
            ))

        bids.sort(key=lambda b: b.bid_amount, reverse=True)
        blackboard.write(self.agent_id, "bids", bids)
        return bids
