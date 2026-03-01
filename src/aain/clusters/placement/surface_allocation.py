from __future__ import annotations

from typing import Any

from aain.core.agent import BaseAgent
from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.types import EventType
from aain.models.creative import RenderSpec
from aain.models.intent import UserState
from aain.models.placement import PlacementDecision, Surface

AVAILABLE_SURFACES = [
    Surface(surface_id="surf_conversational", surface_type="conversational", intrusiveness_level=2),
    Surface(surface_id="surf_inline", surface_type="inline", intrusiveness_level=3),
    Surface(surface_id="surf_sidebar", surface_type="sidebar", intrusiveness_level=1),
    Surface(surface_id="surf_interstitial", surface_type="interstitial", intrusiveness_level=5),
    Surface(surface_id="surf_notification", surface_type="notification", intrusiveness_level=4),
]


class SurfaceAllocationAgent(BaseAgent):
    """Decides which surface to use and manages density rules."""

    @property
    def subscriptions(self) -> list[EventType]:
        return [EventType.PIPELINE_STAGE]

    async def process(self, event: Event, blackboard: Blackboard) -> Any:
        user_state: UserState | None = blackboard.read("user_state")
        fatigue = user_state.ad_fatigue_score if user_state else 0.0

        # Select surface based on fatigue — higher fatigue = less intrusive
        if fatigue > 0.7:
            max_intrusiveness = 1
        elif fatigue > 0.4:
            max_intrusiveness = 2
        elif fatigue > 0.2:
            max_intrusiveness = 3
        else:
            max_intrusiveness = 4

        eligible = [
            s for s in AVAILABLE_SURFACES
            if s.available and s.intrusiveness_level <= max_intrusiveness
        ]

        if not eligible:
            eligible = [AVAILABLE_SURFACES[2]]  # Fallback to sidebar

        surface = eligible[0]
        position = "inline" if surface.surface_type == "conversational" else "top"

        decision = PlacementDecision(
            surface=surface,
            position=position,
            render_spec=RenderSpec(
                format="native" if surface.surface_type == "conversational" else "banner"
            ),
        )
        blackboard.write(self.agent_id, "placement_decision", decision)
        return decision
