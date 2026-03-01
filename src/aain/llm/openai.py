from __future__ import annotations

from aain.llm.base import BaseLLM


class OpenAIAdapter(BaseLLM):
    """OpenAI API adapter (stubbed — install openai SDK and configure API key to use)."""

    def __init__(self, api_key: str = "", model: str = "gpt-4o"):
        self.api_key = api_key
        self.model = model

    async def complete(self, prompt: str, max_tokens: int = 256) -> str:
        raise NotImplementedError(
            "OpenAI adapter not implemented. Set AAIN_LLM_PROVIDER=mock or install openai SDK."
        )

    async def classify(self, text: str, categories: list[str]) -> dict[str, float]:
        raise NotImplementedError("OpenAI adapter not implemented.")

    async def embed(self, text: str) -> list[float]:
        raise NotImplementedError("OpenAI adapter not implemented.")
