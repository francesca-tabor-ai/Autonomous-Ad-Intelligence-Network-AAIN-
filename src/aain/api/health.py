from __future__ import annotations

import time

from fastapi import APIRouter, Request

router = APIRouter()
_start_time = time.time()


@router.get("/health")
async def health(request: Request) -> dict:
    system = request.app.state.system
    return {
        "status": "healthy",
        "uptime_seconds": round(time.time() - _start_time, 1),
        "agent_count": system.registry.agent_count,
        "cluster_count": len(system.registry.all_clusters()),
        "llm_provider": type(system.llm).__name__,
    }


@router.get("/ready")
async def ready(request: Request) -> dict:
    system = request.app.state.system
    return {"ready": system.registry.agent_count > 0}
