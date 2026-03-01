from __future__ import annotations

import time
from typing import Any

from aain.core.agent import BaseAgent
from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.types import EventType
from aain.models.intent import UserState


class UserStateAgent(BaseAgent):
    """Tracks session state, detects buying momentum, estimates conversion probability."""

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._session_store: dict[str, UserState] = {}

    @property
    def subscriptions(self) -> list[EventType]:
        return [EventType.PIPELINE_STAGE]

    async def process(self, event: Event, blackboard: Blackboard) -> Any:
        payload = blackboard.read("trigger_payload", {})
        session_id = payload.get("session_id", "default")
        user_id = payload.get("user_id", "anonymous")
        query = payload.get("query", "")

        existing = self._session_store.get(session_id)

        if existing:
            ads_shown = existing.ads_shown_count
            fatigue = min(1.0, ads_shown / 10.0)
            queries = existing.session_queries + [query]
            engagement = min(1.0, len(queries) * 0.15)
            conversion_prob = self._estimate_conversion(queries, ads_shown)

            state = UserState(
                session_id=session_id,
                user_id=user_id,
                engagement_level=round(engagement, 2),
                ad_fatigue_score=round(fatigue, 2),
                ads_shown_count=ads_shown,
                last_ad_timestamp=existing.last_ad_timestamp,
                session_queries=queries[-20:],
                conversion_probability=round(conversion_prob, 2),
            )
        else:
            state = UserState(
                session_id=session_id,
                user_id=user_id,
                engagement_level=0.15,
                ad_fatigue_score=0.0,
                ads_shown_count=0,
                session_queries=[query],
                conversion_probability=0.1,
            )

        self._session_store[session_id] = state
        blackboard.write(self.agent_id, "user_state", state)
        return state

    def _estimate_conversion(self, queries: list[str], ads_shown: int) -> float:
        base = 0.05
        query_boost = min(0.3, len(queries) * 0.03)
        fatigue_penalty = min(0.2, ads_shown * 0.02)
        return max(0.01, base + query_boost - fatigue_penalty)

    def record_ad_shown(self, session_id: str) -> None:
        state = self._session_store.get(session_id)
        if state:
            self._session_store[session_id] = state.model_copy(update={
                "ads_shown_count": state.ads_shown_count + 1,
                "last_ad_timestamp": time.time(),
                "ad_fatigue_score": min(1.0, (state.ads_shown_count + 1) / 10.0),
            })
