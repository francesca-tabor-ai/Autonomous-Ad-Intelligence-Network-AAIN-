from __future__ import annotations

from typing import Any

from aain.core.agent import BaseAgent
from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.types import EventType
from aain.models.reward import GlobalReward


class RLControllerAgent(BaseAgent):
    """Reinforcement Learning controller.

    Receives reward signals and updates global policy weights
    using exponential moving average (full RL with PPO/A2C is stubbed).
    """

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._reward_history: list[float] = []
        self._ema_reward: float = 0.0
        self._ema_alpha: float = 0.1  # EMA smoothing factor
        self._weight_adjustments: dict[str, float] = {}

    @property
    def subscriptions(self) -> list[EventType]:
        return [EventType.PIPELINE_STAGE, EventType.REWARD_SIGNAL]

    async def process(self, event: Event, blackboard: Blackboard) -> Any:
        reward = blackboard.read("global_reward")

        if isinstance(reward, GlobalReward):
            total = reward.total
        elif isinstance(reward, dict):
            total = reward.get("total", 0.0)
        else:
            total = 0.0

        self._reward_history.append(total)
        if len(self._reward_history) > 1000:
            self._reward_history = self._reward_history[-1000:]

        # EMA update
        self._ema_reward = self._ema_alpha * total + (1 - self._ema_alpha) * self._ema_reward

        # Compute weight adjustments based on reward trend
        if len(self._reward_history) >= 10:
            recent = sum(self._reward_history[-10:]) / 10
            older = sum(self._reward_history[-20:-10]) / 10 if len(self._reward_history) >= 20 else recent

            trend = recent - older
            adjustment = trend * 0.01  # Small adjustment

            self._weight_adjustments = {
                "alpha": adjustment if reward and isinstance(reward, GlobalReward)
                         and reward.revenue_component > 0 else 0.0,
                "beta": adjustment * 0.5,
                "gamma": adjustment * 0.3,
                "delta": adjustment * 0.2,
                "epsilon": -adjustment * 0.1,
            }

        blackboard.write(self.agent_id, "rl_weights", self._weight_adjustments)
        blackboard.write(self.agent_id, "ema_reward", self._ema_reward)

        return {
            "ema_reward": round(self._ema_reward, 4),
            "history_size": len(self._reward_history),
            "adjustments": self._weight_adjustments,
        }

    @property
    def ema_reward(self) -> float:
        return self._ema_reward

    @property
    def reward_history(self) -> list[float]:
        return list(self._reward_history)
