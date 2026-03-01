from __future__ import annotations

from fastapi import APIRouter

from aain.api.health import router as health_router
from aain.api.agents import router as agents_router
from aain.api.pipeline import router as pipeline_router
from aain.api.events import router as events_router
from aain.api.economy import router as economy_router
from aain.api.oversight import router as oversight_router
from aain.api.websocket import router as ws_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["Health"])
api_router.include_router(agents_router, prefix="/agents", tags=["Agents"])
api_router.include_router(pipeline_router, prefix="/pipeline", tags=["Pipeline"])
api_router.include_router(events_router, prefix="/events", tags=["Events"])
api_router.include_router(economy_router, prefix="/economy", tags=["Economy"])
api_router.include_router(oversight_router, prefix="/oversight", tags=["Oversight"])
api_router.include_router(ws_router, tags=["WebSocket"])
