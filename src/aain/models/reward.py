from __future__ import annotations

from pydantic import BaseModel, Field


class GlobalReward(BaseModel):
    revenue_component: float = 0.0
    engagement_component: float = 0.0
    retention_component: float = 0.0
    roas_component: float = 0.0
    trust_erosion_penalty: float = 0.0
    total: float = 0.0
    weights: dict[str, float] = Field(default_factory=lambda: {
        "alpha": 0.3,
        "beta": 0.25,
        "gamma": 0.2,
        "delta": 0.15,
        "epsilon": 0.1,
    })


class AgentReward(BaseModel):
    agent_id: str
    reward_amount: float
    source: str = "pipeline_completion"
    correlation_id: str = ""
