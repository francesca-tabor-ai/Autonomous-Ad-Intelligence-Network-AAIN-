from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "AAIN_"}

    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    llm_provider: str = "mock"  # mock | claude | openai

    # Pipeline
    pipeline_total_budget_ms: int = 300
    event_bus_max_history: int = 10_000
    event_bus_handler_timeout_ms: int = 100

    # Economy
    initial_mint_per_agent: float = 100.0
    economy_base_budget: float = 10.0

    # Reward weights
    reward_alpha: float = 0.3   # Revenue
    reward_beta: float = 0.25   # Engagement
    reward_gamma: float = 0.2   # Retention
    reward_delta: float = 0.15  # Advertiser ROAS
    reward_epsilon: float = 0.1 # Trust erosion penalty


settings = Settings()
