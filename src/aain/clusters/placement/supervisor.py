from __future__ import annotations

from aain.core.cluster import ClusterSupervisor
from aain.core.event_bus import AsyncEventBus
from aain.core.types import ClusterID
from aain.clusters.placement.surface_allocation import SurfaceAllocationAgent
from aain.clusters.placement.conversational import ConversationalInsertionAgent
from aain.llm.base import BaseLLM


class PlacementClusterSupervisor(ClusterSupervisor):
    def __init__(self, event_bus: AsyncEventBus, llm: BaseLLM):
        super().__init__(
            agent_id="placement_supervisor",
            cluster_id=ClusterID.PLACEMENT.value,
            event_bus=event_bus,
        )
        self.register_agent(
            SurfaceAllocationAgent("surface_allocation", self.cluster_id, event_bus)
        )
        self.register_agent(
            ConversationalInsertionAgent("conversational_insertion", self.cluster_id, event_bus, llm)
        )
