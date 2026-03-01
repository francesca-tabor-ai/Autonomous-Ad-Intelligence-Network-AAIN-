from __future__ import annotations

import hashlib
import random

from aain.llm.base import BaseLLM


class MockLLM(BaseLLM):
    """Rule-based mock LLM for development and testing.

    Deterministic responses based on input hashing.
    """

    async def complete(self, prompt: str, max_tokens: int = 256) -> str:
        prompt_lower = prompt.lower()

        if "headline" in prompt_lower or "ad copy" in prompt_lower:
            return "Discover the perfect solution for your needs"
        if "cta" in prompt_lower or "call to action" in prompt_lower:
            return "Get Started Today"
        if "transition" in prompt_lower or "insertion" in prompt_lower:
            return "Speaking of that, you might find this helpful"
        if "body" in prompt_lower:
            return "Trusted by thousands of businesses worldwide. Start your free trial."

        return f"Generated response for: {prompt[:50]}"

    async def classify(self, text: str, categories: list[str]) -> dict[str, float]:
        if not categories:
            return {}

        text_lower = text.lower()
        scores: dict[str, float] = {}

        commercial_keywords = {"buy", "best", "price", "compare", "review", "deal", "cheap", "top"}
        transactional_keywords = {"purchase", "order", "subscribe", "sign up", "download", "get"}
        nav_keywords = {"login", "website", "official", "homepage"}

        words = set(text_lower.split())

        for cat in categories:
            cat_lower = cat.lower()
            if "transactional" in cat_lower and words & transactional_keywords:
                scores[cat] = 0.85
            elif "commercial" in cat_lower and words & commercial_keywords:
                scores[cat] = 0.75
            elif "navigational" in cat_lower and words & nav_keywords:
                scores[cat] = 0.70
            elif "informational" in cat_lower:
                scores[cat] = 0.40
            else:
                h = int(hashlib.md5(f"{text}{cat}".encode()).hexdigest()[:8], 16)
                scores[cat] = (h % 100) / 100.0

        return scores

    async def embed(self, text: str) -> list[float]:
        h = hashlib.sha256(text.encode()).hexdigest()
        return [int(h[i : i + 2], 16) / 255.0 for i in range(0, 64, 2)]
