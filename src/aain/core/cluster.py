from __future__ import annotations

import asyncio
from typing import Any

from aain.core.agent import BaseAgent
from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.event_bus import AsyncEventBus
from aain.core.types import AgentState, EventType


class ClusterSupervisor(BaseAgent):
    """Manages a group of specialist agents within a cluster.

    Orchestrates execution order, aggregates results, handles failures.
    """

    def __init__(self, agent_id: str, cluster_id: str, event_bus: AsyncEventBus):
        super().__init__(agent_id, cluster_id, event_bus)
        self._agents: list[BaseAgent] = []

    @property
    def subscriptions(self) -> list[EventType]:
        return [EventType.PIPELINE_STAGE]

    def register_agent(self, agent: BaseAgent) -> None:
        self._agents.append(agent)

    @property
    def agents(self) -> list[BaseAgent]:
        return list(self._agents)

    async def process(self, event: Event, blackboard: Blackboard) -> Any:
        stage = event.payload.get("stage", "")
        if stage != self.cluster_id:
            return None
        return await self.run_cluster(event, blackboard)

    async def run_cluster(self, event: Event, blackboard: Blackboard) -> dict:
        results: dict[str, Any] = {}
        for agent in self._agents:
            if agent.state == AgentState.PAUSED:
                continue
            try:
                result = await asyncio.wait_for(
                    agent.process(event, blackboard),
                    timeout=0.05,
                )
                results[agent.agent_id] = result
            except asyncio.TimeoutError:
                results[agent.agent_id] = {"error": "timeout"}
                self.log.warning("agent_timeout", agent_id=agent.agent_id)
            except Exception as exc:
                results[agent.agent_id] = {"error": str(exc)}
                self.log.error("agent_error", agent_id=agent.agent_id, error=str(exc))
        return results

    async def start(self) -> None:
        await super().start()
        for agent in self._agents:
            await agent.start()

    async def stop(self) -> None:
        for agent in self._agents:
            await agent.stop()
        await super().stop()
