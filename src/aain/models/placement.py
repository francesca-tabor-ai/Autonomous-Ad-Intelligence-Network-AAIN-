from __future__ import annotations

from pydantic import BaseModel, Field

from aain.models.creative import RenderSpec


class Surface(BaseModel):
    surface_id: str
    surface_type: str  # sidebar, inline, interstitial, conversational, notification
    intrusiveness_level: int = Field(ge=1, le=5)
    available: bool = True


class PlacementDecision(BaseModel):
    surface: Surface
    position: str = "top"
    render_spec: RenderSpec = Field(default_factory=RenderSpec)


class InsertionPoint(BaseModel):
    insertion_type: str = "after_response"
    transition_text: str = ""
    delay_ms: int = 0
    context_relevance_score: float = Field(ge=0.0, le=1.0, default=0.5)
