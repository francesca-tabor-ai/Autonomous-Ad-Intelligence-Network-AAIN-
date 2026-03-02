from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from aain.app import create_app
from aain.main import bootstrap_system


@pytest.fixture
async def client():
    """Create a test client with a fully bootstrapped system.

    ASGITransport does not run FastAPI lifespan, so we manually
    bootstrap the system and attach it to app.state.
    """
    app = create_app()
    system = await bootstrap_system()
    app.state.system = system
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    await system.shutdown()


async def test_health(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["agent_count"] > 0
    assert data["cluster_count"] == 7


async def test_ready(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/ready")
    assert resp.status_code == 200
    assert resp.json()["ready"] is True


async def test_list_agents(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/agents")
    assert resp.status_code == 200
    agents = resp.json()
    assert isinstance(agents, list)
    assert len(agents) > 20  # 21 agents + 7 supervisors


async def test_get_single_agent(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/agents/intent_parser")
    assert resp.status_code == 200
    data = resp.json()
    assert data["agent_id"] == "intent_parser"
    assert "state" in data


async def test_get_missing_agent(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/agents/nonexistent")
    assert resp.status_code == 404


async def test_pause_resume_agent(client: AsyncClient) -> None:
    resp = await client.post("/api/v1/agents/intent_parser/pause")
    assert resp.status_code == 200
    assert resp.json()["state"] == "paused"

    resp = await client.post("/api/v1/agents/intent_parser/resume")
    assert resp.status_code == 200
    assert resp.json()["state"] == "idle"


async def test_execute_pipeline(client: AsyncClient) -> None:
    resp = await client.post("/api/v1/pipeline/execute", json={
        "query": "best CRM for startups",
        "session_id": "api_test",
        "user_id": "api_user",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "correlation_id" in data


async def test_pipeline_stats(client: AsyncClient) -> None:
    # Run a pipeline first
    await client.post("/api/v1/pipeline/execute", json={
        "query": "test query", "session_id": "s1",
    })

    resp = await client.get("/api/v1/pipeline/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "latency" in data


async def test_list_events(client: AsyncClient) -> None:
    # Run a pipeline to generate events
    await client.post("/api/v1/pipeline/execute", json={
        "query": "test", "session_id": "s1",
    })

    resp = await client.get("/api/v1/events")
    assert resp.status_code == 200
    events = resp.json()
    assert isinstance(events, list)


async def test_filter_events_by_type(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/events", params={"type": "pipeline_stage"})
    assert resp.status_code == 200


async def test_economy_balances(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/economy/balances")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert len(data) > 0


async def test_economy_transactions(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/economy/transactions")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_mint_tokens(client: AsyncClient) -> None:
    resp = await client.post("/api/v1/economy/mint", json={
        "agent_id": "intent_parser",
        "amount": 50.0,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["agent_id"] == "intent_parser"
    assert data["new_balance"] > 0


async def test_oversight_audit_log(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/oversight/audit-log")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


async def test_get_reward_weights(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/oversight/reward-weights")
    assert resp.status_code == 200
    data = resp.json()
    assert "alpha" in data
    assert "epsilon" in data


async def test_update_reward_weights(client: AsyncClient) -> None:
    resp = await client.post("/api/v1/oversight/reward-weights", json={
        "alpha": 0.35,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["alpha"] == 0.35


async def test_human_override(client: AsyncClient) -> None:
    resp = await client.post("/api/v1/oversight/override", json={
        "action": "pause_agent",
        "target": "bid_strategy",
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "paused"

    # Clean up
    await client.post("/api/v1/oversight/override", json={
        "action": "resume_agent",
        "target": "bid_strategy",
    })


async def test_bias_report(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/oversight/bias-report")
    assert resp.status_code == 200
    data = resp.json()
    assert "agent_count" in data
    assert "per_agent" in data
