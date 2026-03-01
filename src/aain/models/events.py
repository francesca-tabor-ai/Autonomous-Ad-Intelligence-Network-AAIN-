from __future__ import annotations

from pydantic import BaseModel, Field

from aain.models.auction import AuctionRequest, AuctionResult
from aain.models.performance import Impression, Click, Conversion
from aain.models.policy import ComplianceResult


class IntentEventPayload(BaseModel):
    query: str
    session_id: str
    user_id: str = "anonymous"
    conversation_context: list[str] = Field(default_factory=list)


class AuctionEventPayload(BaseModel):
    auction_request: AuctionRequest | None = None
    auction_result: AuctionResult | None = None


class PerformanceEventPayload(BaseModel):
    impression: Impression | None = None
    click: Click | None = None
    conversion: Conversion | None = None


class ComplianceEventPayload(BaseModel):
    result: ComplianceResult
    campaign_id: str
    action_taken: str = "none"


class RewardEventPayload(BaseModel):
    correlation_id: str
    total_reward: float
    weights: dict[str, float] = Field(default_factory=dict)
