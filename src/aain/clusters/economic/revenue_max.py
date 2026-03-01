from __future__ import annotations

from typing import Any

from aain.core.agent import BaseAgent
from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.types import EventType
from aain.models.auction import AuctionResult, Bid
from aain.models.campaign import Campaign


class RevenueMaximizationAgent(BaseAgent):
    """Runs second-price auction, optimizes yield per intent."""

    @property
    def subscriptions(self) -> list[EventType]:
        return [EventType.PIPELINE_STAGE]

    async def process(self, event: Event, blackboard: Blackboard) -> Any:
        bids: list[Bid] = blackboard.read("bids", [])
        campaigns: list[Campaign] = blackboard.read("candidate_campaigns", [])

        if not bids or len(bids) < 1:
            blackboard.write(self.agent_id, "auction_result", None)
            return None

        reserve_price = 0.01
        eligible = [b for b in bids if b.bid_amount >= reserve_price]
        if not eligible:
            blackboard.write(self.agent_id, "auction_result", None)
            return None

        eligible.sort(key=lambda b: b.bid_amount * b.quality_score, reverse=True)

        winner = eligible[0]
        runner_up = eligible[1] if len(eligible) > 1 else None

        # Second-price: winner pays runner-up's bid + epsilon
        clearing_price = (runner_up.bid_amount + 0.01) if runner_up else reserve_price

        result = AuctionResult(
            winner_campaign_id=winner.campaign_id,
            winning_bid=winner.bid_amount,
            clearing_price=round(clearing_price, 4),
            runner_up_bid=runner_up.bid_amount if runner_up else None,
            participants=len(eligible),
        )

        # Set winning campaign for downstream clusters
        campaign_map = {c.campaign_id: c for c in campaigns}
        winning_campaign = campaign_map.get(winner.campaign_id)
        if winning_campaign:
            blackboard.write(self.agent_id, "winning_campaign", winning_campaign)

        blackboard.write(self.agent_id, "auction_result", result)
        blackboard.write(self.agent_id, "final_price", clearing_price)
        return result
