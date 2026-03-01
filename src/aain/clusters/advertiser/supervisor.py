from __future__ import annotations

from aain.core.cluster import ClusterSupervisor
from aain.core.event_bus import AsyncEventBus
from aain.core.types import ClusterID
from aain.clusters.advertiser.campaign_optimizer import CampaignOptimizerAgent
from aain.clusters.advertiser.bid_strategy import BidStrategyAgent
from aain.clusters.advertiser.audience_expansion import AudienceExpansionAgent


class AdvertiserClusterSupervisor(ClusterSupervisor):
    def __init__(self, event_bus: AsyncEventBus):
        super().__init__(
            agent_id="advertiser_supervisor",
            cluster_id=ClusterID.ADVERTISER.value,
            event_bus=event_bus,
        )
        self.register_agent(CampaignOptimizerAgent("campaign_optimizer", self.cluster_id, event_bus))
        self.register_agent(BidStrategyAgent("bid_strategy", self.cluster_id, event_bus))
        self.register_agent(AudienceExpansionAgent("audience_expansion", self.cluster_id, event_bus))
