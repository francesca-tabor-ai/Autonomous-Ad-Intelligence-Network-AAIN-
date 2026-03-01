from __future__ import annotations

from typing import Any

from aain.core.agent import BaseAgent
from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.types import EventType
from aain.models.intent import CommercialRelevance, IntentSignal, IntentType


INTENT_SCORES = {
    IntentType.TRANSACTIONAL: 0.95,
    IntentType.COMMERCIAL_INVESTIGATION: 0.80,
    IntentType.NAVIGATIONAL: 0.40,
    IntentType.INFORMATIONAL: 0.20,
}


class CommercialRelevanceAgent(BaseAgent):
    """Calculates intent monetization score. Filters non-commercial moments."""

    @property
    def subscriptions(self) -> list[EventType]:
        return [EventType.PIPELINE_STAGE]

    async def process(self, event: Event, blackboard: Blackboard) -> Any:
        intent: IntentSignal | None = blackboard.read("parsed_intent")
        if not intent:
            result = CommercialRelevance(score=0.0, is_eligible=False, reasoning="No intent parsed")
            blackboard.write(self.agent_id, "commercial_relevance", result)
            return result

        base_score = INTENT_SCORES.get(intent.intent_type, 0.2)

        # Boost for categories with high commercial value
        category_boost = 0.05 * len(intent.categories)
        # Boost for high confidence
        confidence_boost = 0.1 if intent.confidence > 0.8 else 0.0

        score = min(1.0, base_score + category_boost + confidence_boost)
        is_eligible = score >= 0.3

        result = CommercialRelevance(
            score=round(score, 2),
            category=intent.categories[0] if intent.categories else "general",
            reasoning=f"Intent={intent.intent_type.value}, confidence={intent.confidence}",
            is_eligible=is_eligible,
        )
        blackboard.write(self.agent_id, "commercial_relevance", result)
        return result
