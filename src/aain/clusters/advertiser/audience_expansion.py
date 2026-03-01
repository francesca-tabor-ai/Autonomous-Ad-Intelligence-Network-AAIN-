from __future__ import annotations

from typing import Any

from aain.core.agent import BaseAgent
from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.types import EventType
from aain.models.intent import IntentSignal

EXPANSION_MAP: dict[str, list[str]] = {
    "saas": ["cloud", "software", "productivity", "business"],
    "crm": ["sales", "marketing", "customer_service"],
    "ecommerce": ["retail", "marketplace", "dropshipping"],
    "finance": ["fintech", "banking", "payments"],
    "education": ["online_learning", "edtech", "professional_development"],
    "travel": ["hospitality", "airlines", "tourism"],
}


class AudienceExpansionAgent(BaseAgent):
    """Finds high-probability adjacent audience segments using similarity modeling."""

    @property
    def subscriptions(self) -> list[EventType]:
        return [EventType.PIPELINE_STAGE]

    async def process(self, event: Event, blackboard: Blackboard) -> Any:
        intent: IntentSignal | None = blackboard.read("parsed_intent")
        if not intent:
            blackboard.write(self.agent_id, "expanded_audiences", {})
            return {}

        expanded: dict[str, list[str]] = {}
        for cat in intent.categories:
            if cat in EXPANSION_MAP:
                expanded[cat] = EXPANSION_MAP[cat]

        blackboard.write(self.agent_id, "expanded_audiences", expanded)
        return expanded
