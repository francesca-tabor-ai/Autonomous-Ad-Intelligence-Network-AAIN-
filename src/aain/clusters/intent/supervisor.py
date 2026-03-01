from __future__ import annotations

from aain.core.cluster import ClusterSupervisor
from aain.core.event_bus import AsyncEventBus
from aain.core.types import ClusterID
from aain.clusters.intent.intent_parser import IntentParserAgent
from aain.clusters.intent.commercial_relevance import CommercialRelevanceAgent
from aain.clusters.intent.user_state import UserStateAgent
from aain.llm.base import BaseLLM


class IntentClusterSupervisor(ClusterSupervisor):
    def __init__(self, event_bus: AsyncEventBus, llm: BaseLLM):
        super().__init__(
            agent_id="intent_supervisor",
            cluster_id=ClusterID.INTENT.value,
            event_bus=event_bus,
        )
        parser = IntentParserAgent("intent_parser", self.cluster_id, event_bus, llm)
        relevance = CommercialRelevanceAgent("commercial_relevance", self.cluster_id, event_bus)
        user_state = UserStateAgent("user_state", self.cluster_id, event_bus)

        self.register_agent(parser)
        self.register_agent(relevance)
        self.register_agent(user_state)
