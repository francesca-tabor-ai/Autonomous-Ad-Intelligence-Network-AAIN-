from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class IntentType(str, Enum):
    TRANSACTIONAL = "transactional"
    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    COMMERCIAL_INVESTIGATION = "commercial_investigation"


class LifecycleStage(str, Enum):
    AWARENESS = "awareness"
    CONSIDERATION = "consideration"
    DECISION = "decision"
    RETENTION = "retention"


class IntentSignal(BaseModel):
    query: str
    intent_type: IntentType
    confidence: float = Field(ge=0.0, le=1.0)
    entities: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    lifecycle_stage: LifecycleStage = LifecycleStage.AWARENESS
    language: str = "en"


class CommercialRelevance(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    category: str = ""
    reasoning: str = ""
    is_eligible: bool = True


class UserState(BaseModel):
    session_id: str
    user_id: str = "anonymous"
    engagement_level: float = Field(ge=0.0, le=1.0, default=0.5)
    ad_fatigue_score: float = Field(ge=0.0, le=1.0, default=0.0)
    ads_shown_count: int = 0
    last_ad_timestamp: float | None = None
    session_queries: list[str] = Field(default_factory=list)
    conversion_probability: float = Field(ge=0.0, le=1.0, default=0.1)
    opt_out: bool = False
