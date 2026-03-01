from __future__ import annotations

from typing import TYPE_CHECKING, Any

from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.event_bus import AsyncEventBus
from aain.core.registry import AgentRegistry
from aain.core.types import ClusterID, EventType
from aain.utils.ids import generate_correlation_id
from aain.utils.logging import get_logger

if TYPE_CHECKING:
    from aain.economy.reward_calculator import RewardCalculator

log = get_logger("strategic_supervisor")


class StrategicSupervisor:
    """Top-level supervisor. Coordinates cluster execution in pipeline order.

    Enforces global reward function, processes human overrides,
    and triggers RL weight updates.
    """

    PIPELINE_ORDER = [
        ClusterID.INTENT,
        ClusterID.POLICY,
        ClusterID.ADVERTISER,
        ClusterID.ECONOMIC,
        ClusterID.CREATIVE,
        ClusterID.PLACEMENT,
        ClusterID.LEARNING,
    ]

    def __init__(
        self,
        registry: AgentRegistry,
        event_bus: AsyncEventBus,
        reward_calculator: RewardCalculator,
    ):
        self.registry = registry
        self.event_bus = event_bus
        self.reward_calculator = reward_calculator
        self._override_active = False

    async def execute_pipeline(self, trigger_payload: dict[str, Any]) -> dict:
        from aain.core.pipeline import PipelineContext

        correlation_id = generate_correlation_id()
        blackboard = Blackboard(correlation_id=correlation_id)
        PipelineContext.set_blackboard(correlation_id, blackboard)
        blackboard.write("pipeline", "trigger_payload", trigger_payload)

        results: dict[str, Any] = {}

        for cluster_id in self.PIPELINE_ORDER:
            if self._override_active:
                break

            cluster = self.registry.get_cluster(cluster_id.value)
            if not cluster:
                continue

            stage_event = Event(
                event_type=EventType.PIPELINE_STAGE,
                source_agent_id="strategic_supervisor",
                correlation_id=correlation_id,
                payload={"stage": cluster_id.value},
            )
            result = await cluster.process(stage_event, blackboard)
            results[cluster_id.value] = result

            if blackboard.read("pipeline_veto"):
                break

        reward = self.reward_calculator.calculate(blackboard)
        blackboard.write("strategic_supervisor", "global_reward", reward)

        PipelineContext.remove_blackboard(correlation_id)

        return {
            "correlation_id": correlation_id,
            "cluster_results": results,
            "global_reward": reward.model_dump() if hasattr(reward, "model_dump") else reward,
            "blackboard": blackboard.snapshot(),
        }

    def activate_override(self) -> None:
        self._override_active = True
        log.warning("override_activated")

    def deactivate_override(self) -> None:
        self._override_active = False
        log.info("override_deactivated")
