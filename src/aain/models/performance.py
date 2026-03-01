from __future__ import annotations

from pydantic import BaseModel


class Impression(BaseModel):
    impression_id: str
    correlation_id: str
    campaign_id: str
    creative_variant_id: str
    surface_id: str
    timestamp: float
    viewable: bool = True


class Click(BaseModel):
    impression_id: str
    timestamp: float


class Conversion(BaseModel):
    impression_id: str
    conversion_type: str  # purchase, signup, lead
    value: float = 0.0
    timestamp: float


class PerformanceMetrics(BaseModel):
    campaign_id: str
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    revenue: float = 0.0
    ctr: float = 0.0
    cvr: float = 0.0
    roas: float = 0.0
