from __future__ import annotations

import pytest

from aain.llm.mock import MockLLM


@pytest.fixture
def llm() -> MockLLM:
    return MockLLM()


async def test_complete_headline(llm: MockLLM) -> None:
    result = await llm.complete("Write a headline for the ad")
    assert isinstance(result, str)
    assert len(result) > 0


async def test_complete_cta(llm: MockLLM) -> None:
    result = await llm.complete("Generate a call to action")
    assert "Today" in result or "Started" in result or "response" in result.lower()


async def test_classify(llm: MockLLM) -> None:
    scores = await llm.classify(
        "buy the best CRM software",
        ["transactional", "informational", "commercial"],
    )
    assert "transactional" in scores
    assert scores["transactional"] > 0


async def test_classify_empty(llm: MockLLM) -> None:
    scores = await llm.classify("hello", [])
    assert scores == {}


async def test_embed(llm: MockLLM) -> None:
    embedding = await llm.embed("test text")
    assert isinstance(embedding, list)
    assert len(embedding) == 32
    assert all(0.0 <= v <= 1.0 for v in embedding)
