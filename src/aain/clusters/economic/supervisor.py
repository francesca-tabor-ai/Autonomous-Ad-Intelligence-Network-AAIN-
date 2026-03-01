from __future__ import annotations

from aain.core.cluster import ClusterSupervisor
from aain.core.event_bus import AsyncEventBus
from aain.core.types import ClusterID
from aain.clusters.economic.revenue_max import RevenueMaximizationAgent
from aain.clusters.economic.pricing_model import PricingModelAgent
from aain.clusters.economic.ltv_prediction import LTVPredictionAgent


class EconomicClusterSupervisor(ClusterSupervisor):
    def __init__(self, event_bus: AsyncEventBus):
        super().__init__(
            agent_id="economic_supervisor",
            cluster_id=ClusterID.ECONOMIC.value,
            event_bus=event_bus,
        )
        self.register_agent(RevenueMaximizationAgent("revenue_max", self.cluster_id, event_bus))
        self.register_agent(PricingModelAgent("pricing_model", self.cluster_id, event_bus))
        self.register_agent(LTVPredictionAgent("ltv_prediction", self.cluster_id, event_bus))
