from __future__ import annotations

import random
from typing import Any

from aain.core.agent import BaseAgent
from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.types import EventType
from aain.models.creative import CreativeVariant


class VariantTestingAgent(BaseAgent):
    """Auto-generates A/B variants using Thompson Sampling stub."""

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._variant_stats: dict[str, dict[str, int]] = {}

    @property
    def subscriptions(self) -> list[EventType]:
        return [EventType.PIPELINE_STAGE]

    async def process(self, event: Event, blackboard: Blackboard) -> Any:
        creative: CreativeVariant | None = blackboard.read("generated_creative")
        if not creative:
            return None

        # Thompson Sampling stub: assign to test group
        campaign_id = creative.campaign_id
        if campaign_id not in self._variant_stats:
            self._variant_stats[campaign_id] = {
                "control": 0, "variant_a": 0, "variant_b": 0,
            }

        # Simple allocation: pick least-served group (exploration)
        stats = self._variant_stats[campaign_id]
        group = min(stats, key=stats.get)  # type: ignore[arg-type]
        stats[group] += 1

        final = creative.model_copy(update={"test_group": group})
        blackboard.write(self.agent_id, "final_creative", final)
        return final
