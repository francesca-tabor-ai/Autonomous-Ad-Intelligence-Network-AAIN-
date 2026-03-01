from __future__ import annotations

import math
from typing import Any

from aain.core.agent import BaseAgent
from aain.core.blackboard import Blackboard
from aain.core.events import Event
from aain.core.types import EventType


class DriftDetectionAgent(BaseAgent):
    """Detects performance anomalies and flags model degradation.

    Monitors rolling averages and triggers alerts when metrics
    deviate more than 2 standard deviations from the moving average.
    """

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._metric_history: dict[str, list[float]] = {
            "revenue": [],
            "engagement": [],
            "trust_erosion": [],
            "latency_ms": [],
        }
        self._window_size = 100

    @property
    def subscriptions(self) -> list[EventType]:
        return [EventType.PIPELINE_STAGE, EventType.PERFORMANCE]

    async def process(self, event: Event, blackboard: Blackboard) -> Any:
        # Collect metrics from blackboard
        price = blackboard.read("final_price", 0.0)
        if isinstance(price, (int, float)):
            self._record("revenue", price)

        user_state = blackboard.read("user_state")
        if user_state and hasattr(user_state, "engagement_level"):
            self._record("engagement", user_state.engagement_level)
            self._record("trust_erosion", user_state.ad_fatigue_score)

        # Check for drift
        alerts: list[dict] = []
        for metric, values in self._metric_history.items():
            if len(values) < 20:
                continue
            alert = self._check_drift(metric, values)
            if alert:
                alerts.append(alert)

        if alerts:
            blackboard.write(self.agent_id, "drift_alerts", alerts)

        return {"alerts": alerts, "metrics_tracked": len(self._metric_history)}

    def _record(self, metric: str, value: float) -> None:
        self._metric_history[metric].append(value)
        if len(self._metric_history[metric]) > self._window_size:
            self._metric_history[metric] = self._metric_history[metric][-self._window_size:]

    def _check_drift(self, metric: str, values: list[float]) -> dict | None:
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std = math.sqrt(variance) if variance > 0 else 0.001

        latest = values[-1]
        z_score = abs(latest - mean) / std

        if z_score > 2.0:
            return {
                "metric": metric,
                "z_score": round(z_score, 2),
                "latest_value": round(latest, 4),
                "mean": round(mean, 4),
                "std": round(std, 4),
                "severity": "critical" if z_score > 3.0 else "warning",
            }
        return None
