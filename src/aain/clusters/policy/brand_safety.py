from __future__ import annotations

from typing import Any

from aain.core.agent import BaseAgent
from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.types import EventType
from aain.models.intent import IntentSignal
from aain.models.policy import BrandSafetyScore

UNSAFE_CATEGORIES = {
    "violence", "adult", "hate_speech", "terrorism",
    "drugs", "self_harm", "controversial",
}

SENSITIVE_KEYWORDS = {
    "kill", "attack", "bomb", "weapon", "porn", "xxx",
    "hack", "exploit", "suicide", "terror",
}


class BrandSafetyAgent(BaseAgent):
    """Prevents unsafe adjacency, filters sensitive contexts."""

    @property
    def subscriptions(self) -> list[EventType]:
        return [EventType.PIPELINE_STAGE]

    async def process(self, event: Event, blackboard: Blackboard) -> Any:
        intent: IntentSignal | None = blackboard.read("parsed_intent")

        flagged: list[str] = []
        score = 1.0

        if intent:
            words = set(intent.query.lower().split())
            matching = words & SENSITIVE_KEYWORDS
            if matching:
                flagged.extend(list(matching))
                score -= len(matching) * 0.3

            for cat in intent.categories:
                if cat in UNSAFE_CATEGORIES:
                    flagged.append(cat)
                    score -= 0.4

        score = max(0.0, min(1.0, score))
        blocked = score < 0.3

        result = BrandSafetyScore(
            score=round(score, 2),
            flagged_categories=flagged,
            blocked=blocked,
        )

        blackboard.write(self.agent_id, "brand_safety_score", result)
        if blocked:
            blackboard.write(self.agent_id, "pipeline_veto", True)

        return result
