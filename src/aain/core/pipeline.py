from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Any, TYPE_CHECKING

from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.event_bus import AsyncEventBus
from aain.core.registry import AgentRegistry
from aain.core.types import EventType
from aain.utils.ids import generate_correlation_id
from aain.utils.logging import get_logger
from aain.utils.metrics import LatencyTracker

if TYPE_CHECKING:
    from aain.economy.reward_calculator import RewardCalculator

log = get_logger("pipeline")


@dataclass
class PipelineStage:
    cluster_id: str
    timeout_ms: float
    is_gate: bool = False


class PipelineContext:
    """Stores blackboards keyed by correlation_id for the duration of pipeline execution."""

    _boards: dict[str, Blackboard] = {}

    @classmethod
    def set_blackboard(cls, cid: str, bb: Blackboard) -> None:
        cls._boards[cid] = bb

    @classmethod
    def get_blackboard(cls, cid: str) -> Blackboard | None:
        return cls._boards.get(cid)

    @classmethod
    def remove_blackboard(cls, cid: str) -> None:
        cls._boards.pop(cid, None)


class DecisionPipeline:
    """Orchestrates the end-to-end ad decision flow.

    Total latency budget: 300ms
      Intent:     40ms
      Policy:     30ms (gate — can veto)
      Advertiser: 50ms
      Economic:   40ms
      Creative:   50ms
      Placement:  40ms
      Learning:   50ms (async, non-blocking)
    """

    STAGES = [
        PipelineStage("intent", timeout_ms=40),
        PipelineStage("policy", timeout_ms=30, is_gate=True),
        PipelineStage("advertiser", timeout_ms=50),
        PipelineStage("economic", timeout_ms=40),
        PipelineStage("creative", timeout_ms=50),
        PipelineStage("placement", timeout_ms=40),
    ]
    ASYNC_TAIL = [
        PipelineStage("learning", timeout_ms=50),
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
        self.latency_tracker = LatencyTracker()

    async def execute(self, intent_payload: dict[str, Any]) -> dict:
        correlation_id = generate_correlation_id()
        blackboard = Blackboard(correlation_id)
        PipelineContext.set_blackboard(correlation_id, blackboard)
        blackboard.write("pipeline", "trigger_payload", intent_payload)

        pipeline_start = time.monotonic()
        stage_timings: dict[str, float] = {}

        for stage in self.STAGES:
            stage_start = time.monotonic()
            cluster = self.registry.get_cluster(stage.cluster_id)
            if not cluster:
                continue

            trigger = Event(
                event_type=EventType.PIPELINE_STAGE,
                source_agent_id="pipeline",
                correlation_id=correlation_id,
                payload={"stage": stage.cluster_id},
            )

            try:
                await asyncio.wait_for(
                    cluster.process(trigger, blackboard),
                    timeout=stage.timeout_ms / 1000.0,
                )
            except asyncio.TimeoutError:
                stage_timings[stage.cluster_id] = stage.timeout_ms
                log.warning("stage_timeout", stage=stage.cluster_id)
                if stage.is_gate:
                    return self._no_ad_result(correlation_id, "gate_timeout", stage_timings)
                continue

            elapsed_ms = (time.monotonic() - stage_start) * 1000
            stage_timings[stage.cluster_id] = round(elapsed_ms, 2)

            if stage.is_gate and blackboard.read("pipeline_veto"):
                total_ms = (time.monotonic() - pipeline_start) * 1000
                self.latency_tracker.record(total_ms)
                return self._no_ad_result(correlation_id, "policy_veto", stage_timings)

        total_ms = (time.monotonic() - pipeline_start) * 1000
        self.latency_tracker.record(total_ms)

        # Fire async tail without blocking
        asyncio.create_task(self._run_async_tail(correlation_id, blackboard))

        return {
            "correlation_id": correlation_id,
            "decision": self._serialize(blackboard.read("placement_decision")),
            "creative": self._serialize(blackboard.read("final_creative")),
            "pricing": blackboard.read("final_price"),
            "pricing_model": blackboard.read("pricing_model"),
            "auction_result": self._serialize(blackboard.read("auction_result")),
            "stage_timings": stage_timings,
            "total_latency_ms": round(total_ms, 2),
        }

    async def _run_async_tail(self, correlation_id: str, blackboard: Blackboard) -> None:
        for stage in self.ASYNC_TAIL:
            cluster = self.registry.get_cluster(stage.cluster_id)
            if cluster:
                trigger = Event(
                    event_type=EventType.PIPELINE_STAGE,
                    source_agent_id="pipeline",
                    correlation_id=correlation_id,
                    payload={"stage": stage.cluster_id},
                )
                try:
                    await asyncio.wait_for(
                        cluster.process(trigger, blackboard),
                        timeout=stage.timeout_ms / 1000.0,
                    )
                except Exception:
                    pass

        reward = self.reward_calculator.calculate(blackboard)
        blackboard.write("pipeline", "global_reward", reward)

        await self.event_bus.publish(Event(
            event_type=EventType.REWARD_SIGNAL,
            source_agent_id="pipeline",
            correlation_id=correlation_id,
            payload=reward.model_dump(),
        ))

        PipelineContext.remove_blackboard(correlation_id)

    def _no_ad_result(
        self, correlation_id: str, reason: str, stage_timings: dict[str, float]
    ) -> dict:
        PipelineContext.remove_blackboard(correlation_id)
        return {
            "correlation_id": correlation_id,
            "decision": None,
            "reason": reason,
            "stage_timings": stage_timings,
        }

    @staticmethod
    def _serialize(obj: Any) -> Any:
        if obj is None:
            return None
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        return obj
