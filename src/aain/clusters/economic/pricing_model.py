from __future__ import annotations

from typing import Any

from aain.core.agent import BaseAgent
from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.types import EventType
from aain.models.auction import Bid
from aain.models.intent import CommercialRelevance


class PricingModelAgent(BaseAgent):
    """Switches between CPM/CPC/CPA/intent-based pricing. Learns advertiser elasticity."""

    @property
    def subscriptions(self) -> list[EventType]:
        return [EventType.PIPELINE_STAGE]

    async def process(self, event: Event, blackboard: Blackboard) -> Any:
        bids: list[Bid] = blackboard.read("bids", [])
        relevance: CommercialRelevance | None = blackboard.read("commercial_relevance")
        final_price = blackboard.read("final_price", 0.0)

        if not bids:
            return None

        winner_bid = bids[0] if bids else None
        if not winner_bid:
            return None

        # Select pricing model based on signals
        score = relevance.score if relevance else 0.5

        if score > 0.85:
            pricing_model = "cpa"
            price_multiplier = 1.2
        elif score > 0.6:
            pricing_model = "cpc"
            price_multiplier = 1.0
        else:
            pricing_model = "cpm"
            price_multiplier = 0.8

        adjusted_price = round(final_price * price_multiplier, 4) if final_price else 0.0

        blackboard.write(self.agent_id, "pricing_model", pricing_model)
        blackboard.write(self.agent_id, "final_price", adjusted_price)
        return {"pricing_model": pricing_model, "adjusted_price": adjusted_price}
