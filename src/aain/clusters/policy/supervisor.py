from __future__ import annotations

from aain.core.cluster import ClusterSupervisor
from aain.core.event_bus import AsyncEventBus
from aain.core.types import ClusterID
from aain.clusters.policy.compliance import ComplianceAgent
from aain.clusters.policy.brand_safety import BrandSafetyAgent
from aain.clusters.policy.trust_guardian import UserTrustGuardianAgent


class PolicyClusterSupervisor(ClusterSupervisor):
    def __init__(self, event_bus: AsyncEventBus):
        super().__init__(
            agent_id="policy_supervisor",
            cluster_id=ClusterID.POLICY.value,
            event_bus=event_bus,
        )
        self.register_agent(ComplianceAgent("compliance", self.cluster_id, event_bus))
        self.register_agent(BrandSafetyAgent("brand_safety", self.cluster_id, event_bus))
        self.register_agent(UserTrustGuardianAgent("trust_guardian", self.cluster_id, event_bus))
