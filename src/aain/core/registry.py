from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aain.core.agent import BaseAgent
    from aain.core.cluster import ClusterSupervisor


class AgentRegistry:
    """Singleton-style registry of all agents in the system."""

    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}
        self._clusters: dict[str, ClusterSupervisor] = {}

    def register(self, agent: BaseAgent) -> None:
        self._agents[agent.agent_id] = agent

    def register_cluster(self, supervisor: ClusterSupervisor) -> None:
        self._clusters[supervisor.cluster_id] = supervisor
        self.register(supervisor)

    def get(self, agent_id: str) -> BaseAgent | None:
        return self._agents.get(agent_id)

    def get_cluster(self, cluster_id: str) -> ClusterSupervisor | None:
        return self._clusters.get(cluster_id)

    def all_agents(self) -> list[BaseAgent]:
        return list(self._agents.values())

    def all_clusters(self) -> list[ClusterSupervisor]:
        return list(self._clusters.values())

    def health_report(self) -> dict:
        return {
            agent_id: agent.metrics for agent_id, agent in self._agents.items()
        }

    @property
    def agent_count(self) -> int:
        return len(self._agents)
