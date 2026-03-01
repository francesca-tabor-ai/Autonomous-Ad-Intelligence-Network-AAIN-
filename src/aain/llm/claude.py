from __future__ import annotations

from aain.llm.base import BaseLLM


class ClaudeAdapter(BaseLLM):
    """Claude API adapter (stubbed — install anthropic SDK and configure API key to use)."""

    def __init__(self, api_key: str = "", model: str = "claude-sonnet-4-20250514"):
        self.api_key = api_key
        self.model = model

    async def complete(self, prompt: str, max_tokens: int = 256) -> str:
        raise NotImplementedError(
            "Claude adapter not implemented. Set AAIN_LLM_PROVIDER=mock or install anthropic SDK."
        )

    async def classify(self, text: str, categories: list[str]) -> dict[str, float]:
        raise NotImplementedError("Claude adapter not implemented.")

    async def embed(self, text: str) -> list[float]:
        raise NotImplementedError("Claude adapter not implemented.")
