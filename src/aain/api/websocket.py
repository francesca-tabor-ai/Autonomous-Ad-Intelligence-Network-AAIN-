from __future__ import annotations

import asyncio
import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from aain.core.events import Event

router = APIRouter()


@router.websocket("/ws/events")
async def event_stream(websocket: WebSocket) -> None:
    await websocket.accept()
    system = websocket.app.state.system

    queue: asyncio.Queue[Event] = asyncio.Queue(maxsize=100)

    async def forward_event(event: Event) -> None:
        try:
            queue.put_nowait(event)
        except asyncio.QueueFull:
            pass  # Drop if client is too slow

    system.event_bus.subscribe("ALL", forward_event)

    try:
        while True:
            event = await queue.get()
            data = {
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "source_agent_id": event.source_agent_id,
                "correlation_id": event.correlation_id,
                "timestamp": event.timestamp.isoformat(),
                "payload_keys": list(event.payload.keys()),
            }
            await websocket.send_json(data)
    except WebSocketDisconnect:
        pass
    finally:
        system.event_bus.unsubscribe("ALL", forward_event)
