from __future__ import annotations

from aain.core.cluster import ClusterSupervisor
from aain.core.event_bus import AsyncEventBus
from aain.core.types import ClusterID
from aain.clusters.learning.rl_controller import RLControllerAgent
from aain.clusters.learning.drift_detection import DriftDetectionAgent


class LearningClusterSupervisor(ClusterSupervisor):
    """Learning & Governance cluster. Also acts as the Strategic Supervisor's observer."""

    def __init__(self, event_bus: AsyncEventBus):
        super().__init__(
            agent_id="learning_supervisor",
            cluster_id=ClusterID.LEARNING.value,
            event_bus=event_bus,
        )
        self.register_agent(RLControllerAgent("rl_controller", self.cluster_id, event_bus))
        self.register_agent(DriftDetectionAgent("drift_detection", self.cluster_id, event_bus))
