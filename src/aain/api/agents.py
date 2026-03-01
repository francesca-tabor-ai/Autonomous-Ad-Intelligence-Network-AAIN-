from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

router = APIRouter()


@router.get("")
async def list_agents(request: Request) -> list[dict]:
    system = request.app.state.system
    return [
        {
            "agent_id": agent.agent_id,
            "cluster_id": agent.cluster_id,
            **agent.metrics,
        }
        for agent in system.registry.all_agents()
    ]


@router.get("/{agent_id}")
async def get_agent(agent_id: str, request: Request) -> dict:
    system = request.app.state.system
    agent = system.registry.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    return {
        "agent_id": agent.agent_id,
        "cluster_id": agent.cluster_id,
        **agent.metrics,
    }


@router.post("/{agent_id}/pause")
async def pause_agent(agent_id: str, request: Request) -> dict:
    system = request.app.state.system
    agent = system.registry.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    agent.pause()
    return {"agent_id": agent_id, "state": agent.state.value}


@router.post("/{agent_id}/resume")
async def resume_agent(agent_id: str, request: Request) -> dict:
    system = request.app.state.system
    agent = system.registry.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    agent.resume()
    return {"agent_id": agent_id, "state": agent.state.value}


@router.get("/{agent_id}/metrics")
async def agent_metrics(agent_id: str, request: Request) -> dict:
    system = request.app.state.system
    agent = system.registry.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    return agent.metrics
