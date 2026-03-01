from __future__ import annotations

from pydantic import BaseModel, Field


class CreativeAsset(BaseModel):
    asset_id: str
    campaign_id: str
    asset_type: str = "image"
    url: str = ""
    tags: list[str] = Field(default_factory=list)


class CreativeVariant(BaseModel):
    variant_id: str
    campaign_id: str
    headline: str
    body: str
    cta_text: str
    asset: CreativeAsset | None = None
    test_group: str = "control"
    personalization_signals: dict[str, str] = Field(default_factory=dict)


class RenderSpec(BaseModel):
    format: str = "native"
    max_width: int = 300
    max_height: int = 250
    allow_animation: bool = False
