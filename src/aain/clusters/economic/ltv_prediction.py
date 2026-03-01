from __future__ import annotations

from typing import Any

from aain.core.agent import BaseAgent
from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.types import EventType
from aain.models.intent import UserState


class LTVPredictionAgent(BaseAgent):
    """Predicts downstream user lifetime value. Adjusts bidding thresholds."""

    @property
    def subscriptions(self) -> list[EventType]:
        return [EventType.PIPELINE_STAGE]

    async def process(self, event: Event, blackboard: Blackboard) -> Any:
        user_state: UserState | None = blackboard.read("user_state")

        if not user_state:
            blackboard.write(self.agent_id, "user_ltv_estimate", 0.0)
            blackboard.write(self.agent_id, "ltv_tier", "low")
            return {"ltv_estimate": 0.0, "tier": "low"}

        engagement = user_state.engagement_level
        conversion_prob = user_state.conversion_probability
        queries = len(user_state.session_queries)

        # Simple tier-based LTV estimation
        ltv_score = engagement * 0.4 + conversion_prob * 0.4 + min(queries / 10, 1.0) * 0.2

        if ltv_score > 0.7:
            tier = "high"
            ltv_estimate = 50.0
        elif ltv_score > 0.4:
            tier = "medium"
            ltv_estimate = 20.0
        else:
            tier = "low"
            ltv_estimate = 5.0

        # Adjust ROAS estimate
        final_price = blackboard.read("final_price", 0.0)
        if isinstance(final_price, (int, float)) and final_price > 0:
            estimated_roas = ltv_estimate / final_price
        else:
            estimated_roas = 2.0

        blackboard.write(self.agent_id, "user_ltv_estimate", ltv_estimate)
        blackboard.write(self.agent_id, "ltv_tier", tier)
        blackboard.write(self.agent_id, "estimated_roas", round(estimated_roas, 2))

        return {"ltv_estimate": ltv_estimate, "tier": tier, "estimated_roas": estimated_roas}
