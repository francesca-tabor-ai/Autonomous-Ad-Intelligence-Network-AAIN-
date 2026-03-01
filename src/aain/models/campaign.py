from __future__ import annotations

from pydantic import BaseModel, Field


class Creative(BaseModel):
    creative_id: str
    headline: str
    body: str
    cta_text: str = "Learn More"
    image_url: str | None = None
    template: str = "default"


class Campaign(BaseModel):
    campaign_id: str
    advertiser_id: str
    name: str
    status: str = "active"
    budget_total: float
    budget_remaining: float
    bid_floor: float = 0.01
    bid_ceiling: float = 100.0
    base_bid: float = 1.0
    targeting_categories: list[str] = Field(default_factory=list)
    creatives: list[Creative] = Field(default_factory=list)
    pricing_model: str = "cpm"
    daily_frequency_cap: int = 3
    roas_target: float = 2.0


class Advertiser(BaseModel):
    advertiser_id: str
    name: str
    campaigns: list[str] = Field(default_factory=list)
    total_spend: float = 0.0
    trust_score: float = Field(ge=0.0, le=1.0, default=1.0)
