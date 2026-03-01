from __future__ import annotations

from aain.core.cluster import ClusterSupervisor
from aain.core.event_bus import AsyncEventBus
from aain.core.types import ClusterID
from aain.clusters.creative.dynamic_creative import DynamicCreativeGeneratorAgent
from aain.clusters.creative.asset_selection import AssetSelectionAgent
from aain.clusters.creative.variant_testing import VariantTestingAgent
from aain.llm.base import BaseLLM


class CreativeClusterSupervisor(ClusterSupervisor):
    def __init__(self, event_bus: AsyncEventBus, llm: BaseLLM):
        super().__init__(
            agent_id="creative_supervisor",
            cluster_id=ClusterID.CREATIVE.value,
            event_bus=event_bus,
        )
        self.register_agent(
            DynamicCreativeGeneratorAgent("dynamic_creative", self.cluster_id, event_bus, llm)
        )
        self.register_agent(AssetSelectionAgent("asset_selection", self.cluster_id, event_bus))
        self.register_agent(VariantTestingAgent("variant_testing", self.cluster_id, event_bus))
