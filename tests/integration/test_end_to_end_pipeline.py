from __future__ import annotations

import pytest

from aain.main import bootstrap_system


async def test_full_pipeline_crm_query() -> None:
    system = await bootstrap_system()

    result = await system.pipeline.execute({
        "query": "What's the best CRM for startups?",
        "session_id": "test_session",
        "user_id": "test_user",
    })

    assert "correlation_id" in result
    assert result.get("decision") is not None or result.get("reason") is not None

    if result.get("decision"):
        assert "total_latency_ms" in result
        assert result["creative"] is not None
        assert result["pricing"] is not None or result["pricing"] == 0

    await system.shutdown()


async def test_full_pipeline_informational_query() -> None:
    system = await bootstrap_system()

    result = await system.pipeline.execute({
        "query": "how does photosynthesis work",
        "session_id": "test_session_2",
        "user_id": "test_user_2",
    })

    assert "correlation_id" in result
    await system.shutdown()


async def test_pipeline_latency_budget() -> None:
    system = await bootstrap_system()

    result = await system.pipeline.execute({
        "query": "best project management software",
        "session_id": "test_session_3",
        "user_id": "test_user_3",
    })

    if "total_latency_ms" in result:
        # Pipeline should complete well under 300ms with mock LLM
        assert result["total_latency_ms"] < 300

    await system.shutdown()


async def test_pipeline_multiple_queries() -> None:
    system = await bootstrap_system()

    queries = [
        "best CRM for startups",
        "compare Salesforce vs HubSpot",
        "how to build an online store",
        "top cloud computing services",
    ]

    for query in queries:
        result = await system.pipeline.execute({
            "query": query,
            "session_id": "multi_session",
            "user_id": "multi_user",
        })
        assert "correlation_id" in result

    await system.shutdown()
