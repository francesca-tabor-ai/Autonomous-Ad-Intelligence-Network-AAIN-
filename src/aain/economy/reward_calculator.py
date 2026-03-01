from __future__ import annotations

from aain.core.blackboard import Blackboard
from aain.models.intent import UserState
from aain.models.reward import GlobalReward


class RewardCalculator:
    """Implements the global reward function.

    Global Reward = alpha*Revenue + beta*Engagement
                  + gamma*Retention + delta*ROAS
                  - epsilon*TrustErosion
    """

    def __init__(self, weights: dict[str, float] | None = None):
        self.weights = weights or {
            "alpha": 0.3,
            "beta": 0.25,
            "gamma": 0.2,
            "delta": 0.15,
            "epsilon": 0.1,
        }

    def calculate(self, blackboard: Blackboard) -> GlobalReward:
        price = blackboard.read("final_price", 0.0)
        if not isinstance(price, (int, float)):
            price = 0.0

        user_state = blackboard.read("user_state")
        if isinstance(user_state, UserState):
            engagement = user_state.engagement_level
            fatigue = user_state.ad_fatigue_score
        else:
            engagement = 0.5
            fatigue = 0.0

        retention = 1.0 - fatigue
        roas = blackboard.read("estimated_roas", 1.0)
        if not isinstance(roas, (int, float)):
            roas = 1.0
        trust_erosion = fatigue * 0.5

        w = self.weights
        total = (
            w["alpha"] * min(price / 10.0, 1.0)
            + w["beta"] * engagement
            + w["gamma"] * retention
            + w["delta"] * min(roas / 5.0, 1.0)
            - w["epsilon"] * trust_erosion
        )

        return GlobalReward(
            revenue_component=price,
            engagement_component=engagement,
            retention_component=retention,
            roas_component=roas,
            trust_erosion_penalty=trust_erosion,
            total=round(total, 4),
            weights=dict(w),
        )

    def update_weights(self, adjustment: dict[str, float]) -> None:
        for key, delta in adjustment.items():
            if key in self.weights:
                self.weights[key] = max(0.0, min(1.0, self.weights[key] + delta))
