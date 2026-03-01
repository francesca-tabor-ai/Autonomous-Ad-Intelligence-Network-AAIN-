from __future__ import annotations

from typing import Any

from aain.core.agent import BaseAgent
from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.event_bus import AsyncEventBus
from aain.core.types import EventType
from aain.llm.base import BaseLLM
from aain.models.campaign import Campaign
from aain.models.creative import CreativeVariant
from aain.models.intent import IntentSignal
from aain.utils.ids import generate_id


class DynamicCreativeGeneratorAgent(BaseAgent):
    """Generates tailored ad copy, adjusts tone to match conversation."""

    def __init__(self, agent_id: str, cluster_id: str, event_bus: AsyncEventBus, llm: BaseLLM):
        super().__init__(agent_id, cluster_id, event_bus)
        self.llm = llm

    @property
    def subscriptions(self) -> list[EventType]:
        return [EventType.PIPELINE_STAGE]

    async def process(self, event: Event, blackboard: Blackboard) -> Any:
        winning = blackboard.read("winning_campaign")
        if not winning:
            candidates = blackboard.read("candidate_campaigns", [])
            winning = candidates[0] if candidates else None

        intent: IntentSignal | None = blackboard.read("parsed_intent")
        if not winning or not intent:
            return None

        campaign: Campaign = winning
        base_creative = campaign.creatives[0] if campaign.creatives else None

        if base_creative:
            headline = base_creative.headline
            body = base_creative.body
            cta = base_creative.cta_text
        else:
            headline = await self.llm.complete(
                f"Write a short ad headline for: {campaign.name} targeting: {intent.query}"
            )
            body = await self.llm.complete(
                f"Write ad body copy for: {campaign.name}"
            )
            cta = await self.llm.complete(
                f"Write a call to action for: {campaign.name}"
            )

        # Personalize based on intent
        signals: dict[str, str] = {
            "query": intent.query,
            "intent_type": intent.intent_type.value,
            "lifecycle": intent.lifecycle_stage.value,
        }

        variant = CreativeVariant(
            variant_id=generate_id(),
            campaign_id=campaign.campaign_id,
            headline=headline,
            body=body,
            cta_text=cta,
            personalization_signals=signals,
        )
        blackboard.write(self.agent_id, "generated_creative", variant)
        return variant
