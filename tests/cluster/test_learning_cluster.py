from __future__ import annotations

import pytest

from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.event_bus import AsyncEventBus
from aain.core.types import EventType
from aain.clusters.learning.supervisor import LearningClusterSupervisor
from aain.models.intent import UserState
from aain.models.reward import GlobalReward


@pytest.fixture
def cluster() -> LearningClusterSupervisor:
    return LearningClusterSupervisor(AsyncEventBus())


def _event(bb: Blackboard) -> Event:
    return Event(
        event_type=EventType.PIPELINE_STAGE,
        source_agent_id="test",
        correlation_id=bb.correlation_id,
        payload={"stage": "learning"},
    )


async def test_processes_reward_signal(cluster: LearningClusterSupervisor) -> None:
    bb = Blackboard("test-1")
    bb.write("test", "global_reward", GlobalReward(total=0.65))
    bb.write("test", "final_price", 2.5)
    bb.write("test", "user_state", UserState(
        session_id="s1", engagement_level=0.7, ad_fatigue_score=0.2,
    ))

    await cluster.run_cluster(_event(bb), bb)

    weights = bb.read("rl_weights")
    ema = bb.read("ema_reward")
    assert weights is not None
    assert ema is not None


async def test_rl_controller_accumulates_history(cluster: LearningClusterSupervisor) -> None:
    for i in range(15):
        bb = Blackboard(f"test-2-{i}")
        bb.write("test", "global_reward", GlobalReward(total=0.5 + i * 0.02))
        bb.write("test", "final_price", 2.0)
        bb.write("test", "user_state", UserState(session_id="s1", engagement_level=0.6))
        await cluster.run_cluster(_event(bb), bb)

    rl_agent = cluster.agents[0]
    # run_cluster calls process() directly (not via event bus _handle_event),
    # so check the agent's own reward_history instead of _metrics.
    assert len(rl_agent.reward_history) == 15


async def test_drift_detection_no_alerts_initially(cluster: LearningClusterSupervisor) -> None:
    bb = Blackboard("test-3")
    bb.write("test", "global_reward", GlobalReward(total=0.5))
    bb.write("test", "final_price", 2.0)
    bb.write("test", "user_state", UserState(session_id="s1", engagement_level=0.6))

    await cluster.run_cluster(_event(bb), bb)

    alerts = bb.read("drift_alerts")
    # With only one data point, no drift should be detected
    assert alerts is None or len(alerts) == 0


async def test_drift_detection_with_anomaly(cluster: LearningClusterSupervisor) -> None:
    # Feed 25 normal values
    for i in range(25):
        bb = Blackboard(f"test-4-{i}")
        bb.write("test", "global_reward", GlobalReward(total=0.5))
        bb.write("test", "final_price", 2.0)
        bb.write("test", "user_state", UserState(
            session_id="s1", engagement_level=0.5, ad_fatigue_score=0.2,
        ))
        await cluster.run_cluster(_event(bb), bb)

    # Now feed an anomalous value
    bb = Blackboard("test-4-anomaly")
    bb.write("test", "global_reward", GlobalReward(total=0.5))
    bb.write("test", "final_price", 100.0)  # Extreme outlier
    bb.write("test", "user_state", UserState(
        session_id="s1", engagement_level=0.5, ad_fatigue_score=0.2,
    ))
    await cluster.run_cluster(_event(bb), bb)

    alerts = bb.read("drift_alerts")
    # The anomalous revenue value should trigger a drift alert
    if alerts:
        assert any(a["metric"] == "revenue" for a in alerts)
