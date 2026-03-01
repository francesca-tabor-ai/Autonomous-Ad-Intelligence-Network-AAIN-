from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


@router.get("/audit-log")
async def audit_log(request: Request, limit: int = 100) -> list[dict]:
    system = request.app.state.system
    # Collect audit entries from event bus compliance events
    events = system.event_bus.get_history(limit=limit)
    return [
        {
            "event_id": e.event_id,
            "event_type": e.event_type.value,
            "source": e.source_agent_id,
            "timestamp": e.timestamp.isoformat(),
            "correlation_id": e.correlation_id,
        }
        for e in events
    ]


class OverrideRequest(BaseModel):
    action: str  # pause_agent, resume_agent, veto_campaign, adjust_weights
    target: str = ""
    params: dict = {}


@router.post("/override")
async def human_override(body: OverrideRequest, request: Request) -> dict:
    system = request.app.state.system

    if body.action == "pause_agent":
        agent = system.registry.get(body.target)
        if agent:
            agent.pause()
            return {"status": "paused", "agent_id": body.target}

    elif body.action == "resume_agent":
        agent = system.registry.get(body.target)
        if agent:
            agent.resume()
            return {"status": "resumed", "agent_id": body.target}

    elif body.action == "adjust_weights":
        system.reward_calculator.update_weights(body.params)
        return {"status": "weights_updated", "new_weights": system.reward_calculator.weights}

    return {"status": "unknown_action", "action": body.action}


@router.get("/reward-weights")
async def get_reward_weights(request: Request) -> dict:
    system = request.app.state.system
    return system.reward_calculator.weights


class WeightsUpdate(BaseModel):
    alpha: float | None = None
    beta: float | None = None
    gamma: float | None = None
    delta: float | None = None
    epsilon: float | None = None


@router.post("/reward-weights")
async def update_reward_weights(body: WeightsUpdate, request: Request) -> dict:
    system = request.app.state.system
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    # Direct set (not delta)
    for k, v in updates.items():
        if k in system.reward_calculator.weights:
            system.reward_calculator.weights[k] = v
    return system.reward_calculator.weights


@router.get("/bias-report")
async def bias_report(request: Request) -> dict:
    system = request.app.state.system
    health = system.registry.health_report()
    return {
        "agent_count": len(health),
        "agents_in_error": sum(
            1 for m in health.values() if m.get("state") == "error"
        ),
        "agents_paused": sum(
            1 for m in health.values() if m.get("state") == "paused"
        ),
        "per_agent": health,
    }
