from __future__ import annotations

from pydantic import BaseModel, Field


class Bid(BaseModel):
    campaign_id: str
    advertiser_id: str
    bid_amount: float = Field(ge=0.0)
    bid_type: str = "cpm"
    relevance_score: float = Field(ge=0.0, le=1.0)
    quality_score: float = Field(ge=0.0, le=1.0, default=0.5)


class AuctionRequest(BaseModel):
    correlation_id: str
    bids: list[Bid]
    reserve_price: float = 0.01
    auction_type: str = "second_price"


class AuctionResult(BaseModel):
    winner_campaign_id: str
    winning_bid: float
    clearing_price: float
    runner_up_bid: float | None = None
    participants: int
