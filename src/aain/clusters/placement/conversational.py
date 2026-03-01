from __future__ import annotations

from typing import Any

from aain.core.agent import BaseAgent
from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.event_bus import AsyncEventBus
from aain.core.types import EventType
from aain.llm.base import BaseLLM
from aain.models.intent import IntentSignal
from aain.models.placement import InsertionPoint, PlacementDecision


class ConversationalInsertionAgent(BaseAgent):
    """Integrates sponsored content naturally. Applies disclosure logic."""

    def __init__(self, agent_id: str, cluster_id: str, event_bus: AsyncEventBus, llm: BaseLLM):
        super().__init__(agent_id, cluster_id, event_bus)
        self.llm = llm

    @property
    def subscriptions(self) -> list[EventType]:
        return [EventType.PIPELINE_STAGE]

    async def process(self, event: Event, blackboard: Blackboard) -> Any:
        placement: PlacementDecision | None = blackboard.read("placement_decision")
        intent: IntentSignal | None = blackboard.read("parsed_intent")

        if not placement:
            return None

        is_conversational = placement.surface.surface_type == "conversational"

        if is_conversational and intent:
            transition = await self.llm.complete(
                f"Write a natural transition to sponsored content about: {intent.query}"
            )
            relevance = 0.8
        else:
            transition = "Sponsored"
            relevance = 0.5

        insertion = InsertionPoint(
            insertion_type="inline" if is_conversational else "after_response",
            transition_text=transition,
            delay_ms=0 if is_conversational else 200,
            context_relevance_score=relevance,
        )
        blackboard.write(self.agent_id, "insertion_point", insertion)
        return insertion
