from __future__ import annotations

from fastapi import APIRouter, Request

from aain.core.types import EventType

router = APIRouter()


@router.get("")
async def list_events(
    request: Request, type: str | None = None, limit: int = 50
) -> list[dict]:
    system = request.app.state.system
    event_type = None
    if type:
        try:
            event_type = EventType(type)
        except ValueError:
            pass

    events = system.event_bus.get_history(event_type=event_type, limit=limit)
    return [
        {
            "event_id": e.event_id,
            "event_type": e.event_type.value,
            "source_agent_id": e.source_agent_id,
            "correlation_id": e.correlation_id,
            "timestamp": e.timestamp.isoformat(),
            "payload_keys": list(e.payload.keys()),
        }
        for e in events
    ]


@router.get("/{event_id}")
async def get_event(event_id: str, request: Request) -> dict:
    system = request.app.state.system
    events = system.event_bus.get_history(limit=10000)
    for e in events:
        if e.event_id == event_id:
            return {
                "event_id": e.event_id,
                "event_type": e.event_type.value,
                "source_agent_id": e.source_agent_id,
                "correlation_id": e.correlation_id,
                "timestamp": e.timestamp.isoformat(),
                "payload": e.payload,
            }
    return {"error": "Event not found"}
