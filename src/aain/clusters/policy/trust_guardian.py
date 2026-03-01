from __future__ import annotations

from typing import Any

from aain.core.agent import BaseAgent
from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.types import EventType
from aain.models.intent import UserState
from aain.models.policy import TrustAssessment


class UserTrustGuardianAgent(BaseAgent):
    """Monitors churn signals, suppresses aggressive monetization."""

    @property
    def subscriptions(self) -> list[EventType]:
        return [EventType.PIPELINE_STAGE]

    async def process(self, event: Event, blackboard: Blackboard) -> Any:
        user_state: UserState | None = blackboard.read("user_state")

        if not user_state:
            result = TrustAssessment(approved=True, action="serve", reasoning="No user state")
            blackboard.write(self.agent_id, "trust_assessment", result)
            return result

        if user_state.opt_out:
            result = TrustAssessment(
                approved=False, action="block",
                reasoning="User has opted out of ads",
            )
            blackboard.write(self.agent_id, "trust_assessment", result)
            blackboard.write(self.agent_id, "pipeline_veto", True)
            return result

        fatigue = user_state.ad_fatigue_score
        ads_shown = user_state.ads_shown_count

        if fatigue > 0.8 or ads_shown >= 10:
            result = TrustAssessment(
                approved=False, action="block",
                reasoning=f"High fatigue ({fatigue}) or too many ads ({ads_shown})",
                fatigue_override=True,
            )
            blackboard.write(self.agent_id, "trust_assessment", result)
            blackboard.write(self.agent_id, "pipeline_veto", True)
            return result

        if fatigue > 0.5:
            result = TrustAssessment(
                approved=True, action="downgrade",
                reasoning=f"Moderate fatigue ({fatigue}), downgrading placement",
            )
        else:
            result = TrustAssessment(
                approved=True, action="serve",
                reasoning="User state within acceptable thresholds",
            )

        blackboard.write(self.agent_id, "trust_assessment", result)
        return result
