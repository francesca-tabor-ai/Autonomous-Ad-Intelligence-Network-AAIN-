from __future__ import annotations

import abc


class BaseLLM(abc.ABC):
    """Abstract interface for LLM providers."""

    @abc.abstractmethod
    async def complete(self, prompt: str, max_tokens: int = 256) -> str:
        """Generate text completion."""
        ...

    @abc.abstractmethod
    async def classify(self, text: str, categories: list[str]) -> dict[str, float]:
        """Classify text into categories with confidence scores."""
        ...

    @abc.abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Generate text embedding."""
        ...
