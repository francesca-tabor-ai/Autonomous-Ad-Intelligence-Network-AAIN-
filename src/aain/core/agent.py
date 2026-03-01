from __future__ import annotations

import abc
import asyncio
from typing import Any

from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.event_bus import AsyncEventBus
from aain.core.types import AgentState, EventType
from aain.utils.logging import get_logger


class BaseAgent(abc.ABC):
    """Abstract base for all specialist agents.

    Lifecycle: init -> start -> (process events) -> pause/resume -> stop

    Every agent:
    - Has a unique agent_id and belongs to a cluster_id
    - Subscribes to specific EventTypes
    - Implements process(event, blackboard) as core logic
    - Reports metrics (latency, invocations, errors)
    """

    def __init__(self, agent_id: str, cluster_id: str, event_bus: AsyncEventBus):
        self.agent_id = agent_id
        self.cluster_id = cluster_id
        self.event_bus = event_bus
        self.state = AgentState.IDLE
        self.log = get_logger(agent_id)
        self._metrics = {
            "invocations": 0,
            "total_latency_ms": 0.0,
            "errors": 0,
        }

    @property
    @abc.abstractmethod
    def subscriptions(self) -> list[EventType]:
        ...

    @abc.abstractmethod
    async def process(self, event: Event, blackboard: Blackboard) -> Any:
        ...

    async def start(self) -> None:
        self.state = AgentState.IDLE
        for event_type in self.subscriptions:
            self.event_bus.subscribe(event_type, self._handle_event)

    async def stop(self) -> None:
        self.state = AgentState.TERMINATED
        for event_type in self.subscriptions:
            self.event_bus.unsubscribe(event_type, self._handle_event)

    def pause(self) -> None:
        self.state = AgentState.PAUSED

    def resume(self) -> None:
        if self.state == AgentState.PAUSED:
            self.state = AgentState.IDLE

    async def _handle_event(self, event: Event) -> None:
        if self.state in (AgentState.PAUSED, AgentState.TERMINATED):
            return
        self.state = AgentState.PROCESSING
        self._metrics["invocations"] += 1
        start = asyncio.get_event_loop().time()
        try:
            from aain.core.pipeline import PipelineContext

            blackboard = PipelineContext.get_blackboard(event.correlation_id)
            if blackboard:
                await self.process(event, blackboard)
        except Exception as exc:
            self._metrics["errors"] += 1
            self.state = AgentState.ERROR
            self.log.error("agent_error", error=str(exc))
        finally:
            elapsed = (asyncio.get_event_loop().time() - start) * 1000
            self._metrics["total_latency_ms"] += elapsed
            if self.state == AgentState.PROCESSING:
                self.state = AgentState.IDLE

    @property
    def metrics(self) -> dict:
        inv = self._metrics["invocations"]
        avg = self._metrics["total_latency_ms"] / inv if inv > 0 else 0.0
        return {
            **self._metrics,
            "avg_latency_ms": round(avg, 2),
            "state": self.state.value,
        }

    async def emit(
        self, event_type: EventType, payload: dict[str, Any], correlation_id: str
    ) -> None:
        event = Event(
            event_type=event_type,
            source_agent_id=self.agent_id,
            correlation_id=correlation_id,
            payload=payload,
        )
        await self.event_bus.publish(event)
