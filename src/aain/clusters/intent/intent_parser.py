from __future__ import annotations

from typing import Any

from aain.core.agent import BaseAgent
from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.event_bus import AsyncEventBus
from aain.core.types import EventType
from aain.llm.base import BaseLLM
from aain.models.intent import IntentSignal, IntentType, LifecycleStage

COMMERCIAL_KEYWORDS = {
    "buy", "best", "price", "compare", "review", "deal", "cheap",
    "top", "vs", "alternative", "recommendation", "affordable",
}
TRANSACTIONAL_KEYWORDS = {
    "purchase", "order", "subscribe", "sign up", "download",
    "get", "buy now", "free trial", "pricing",
}
NAVIGATIONAL_KEYWORDS = {"login", "website", "official", "homepage", "sign in"}

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "saas": ["crm", "erp", "saas", "software", "platform", "tool", "app"],
    "ecommerce": ["shop", "store", "buy", "product", "deal"],
    "finance": ["bank", "invest", "loan", "credit", "insurance"],
    "travel": ["hotel", "flight", "travel", "booking", "vacation"],
    "education": ["course", "learn", "tutorial", "training", "certification"],
}


class IntentParserAgent(BaseAgent):
    """Extracts semantic intent, scores commercial likelihood, maps to taxonomy."""

    def __init__(self, agent_id: str, cluster_id: str, event_bus: AsyncEventBus, llm: BaseLLM):
        super().__init__(agent_id, cluster_id, event_bus)
        self.llm = llm

    @property
    def subscriptions(self) -> list[EventType]:
        return [EventType.PIPELINE_STAGE]

    async def process(self, event: Event, blackboard: Blackboard) -> Any:
        payload = blackboard.read("trigger_payload", {})
        query = payload.get("query", "")
        words = set(query.lower().split())

        intent_type = self._classify_intent(words)
        confidence = self._calculate_confidence(words, intent_type)
        entities = self._extract_entities(query)
        categories = self._extract_categories(words)
        lifecycle = self._detect_lifecycle(words, intent_type)

        signal = IntentSignal(
            query=query,
            intent_type=intent_type,
            confidence=confidence,
            entities=entities,
            categories=categories,
            lifecycle_stage=lifecycle,
        )
        blackboard.write(self.agent_id, "parsed_intent", signal)
        return signal

    def _classify_intent(self, words: set[str]) -> IntentType:
        if words & TRANSACTIONAL_KEYWORDS:
            return IntentType.TRANSACTIONAL
        if words & COMMERCIAL_KEYWORDS:
            return IntentType.COMMERCIAL_INVESTIGATION
        if words & NAVIGATIONAL_KEYWORDS:
            return IntentType.NAVIGATIONAL
        return IntentType.INFORMATIONAL

    def _calculate_confidence(self, words: set[str], intent_type: IntentType) -> float:
        keyword_sets = {
            IntentType.TRANSACTIONAL: TRANSACTIONAL_KEYWORDS,
            IntentType.COMMERCIAL_INVESTIGATION: COMMERCIAL_KEYWORDS,
            IntentType.NAVIGATIONAL: NAVIGATIONAL_KEYWORDS,
        }
        matching = keyword_sets.get(intent_type, set())
        overlap = len(words & matching)
        if overlap >= 3:
            return 0.95
        if overlap >= 2:
            return 0.85
        if overlap >= 1:
            return 0.70
        return 0.50

    def _extract_entities(self, query: str) -> list[str]:
        words = query.split()
        return [w for w in words if len(w) > 3 and w[0].isupper()]

    def _extract_categories(self, words: set[str]) -> list[str]:
        categories = []
        for cat, keywords in CATEGORY_KEYWORDS.items():
            if words & set(keywords):
                categories.append(cat)
        return categories

    def _detect_lifecycle(self, words: set[str], intent_type: IntentType) -> LifecycleStage:
        if intent_type == IntentType.TRANSACTIONAL:
            return LifecycleStage.DECISION
        if intent_type == IntentType.COMMERCIAL_INVESTIGATION:
            return LifecycleStage.CONSIDERATION
        if words & {"how", "what", "why", "learn", "guide"}:
            return LifecycleStage.AWARENESS
        return LifecycleStage.AWARENESS
