from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

router = APIRouter()


class PipelineRequest(BaseModel):
    query: str
    session_id: str = "default"
    user_id: str = "anonymous"
    conversation_context: list[str] = Field(default_factory=list)


@router.post("/execute")
async def execute_pipeline(body: PipelineRequest, request: Request) -> dict:
    system = request.app.state.system
    result = await system.pipeline.execute({
        "query": body.query,
        "session_id": body.session_id,
        "user_id": body.user_id,
        "conversation_context": body.conversation_context,
    })
    return result


@router.get("/stats")
async def pipeline_stats(request: Request) -> dict:
    system = request.app.state.system
    return {
        "latency": system.pipeline.latency_tracker.summary(),
    }
