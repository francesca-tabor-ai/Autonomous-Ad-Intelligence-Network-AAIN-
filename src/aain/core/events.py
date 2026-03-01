from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field

from aain.core.types import EventType
from aain.utils.ids import generate_event_id, generate_correlation_id


class Event(BaseModel):
    """Immutable event envelope. Every message on the bus is an Event."""

    model_config = {"frozen": True}

    event_id: str = Field(default_factory=generate_event_id)
    event_type: EventType
    source_agent_id: str
    correlation_id: str = Field(default_factory=generate_correlation_id)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict[str, Any] = Field(default_factory=dict)
    ttl_ms: int = 300
    priority: int = 0
