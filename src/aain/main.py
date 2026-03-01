from __future__ import annotations

import asyncio
from dataclasses import dataclass

from aain.config import settings
from aain.core.event_bus import AsyncEventBus
from aain.core.pipeline import DecisionPipeline
from aain.core.registry import AgentRegistry
from aain.economy.reward_calculator import RewardCalculator
from aain.economy.token_ledger import TokenLedger
from aain.economy.budget_manager import BudgetManager
from aain.economy.internal_auction import InternalAuction
from aain.llm.base import BaseLLM
from aain.llm.mock import MockLLM
from aain.clusters.intent.supervisor import IntentClusterSupervisor
from aain.clusters.policy.supervisor import PolicyClusterSupervisor
from aain.clusters.advertiser.supervisor import AdvertiserClusterSupervisor
from aain.clusters.economic.supervisor import EconomicClusterSupervisor
from aain.clusters.creative.supervisor import CreativeClusterSupervisor
from aain.clusters.placement.supervisor import PlacementClusterSupervisor
from aain.clusters.learning.supervisor import LearningClusterSupervisor
from aain.utils.logging import setup_logging, get_logger

log = get_logger("main")


def get_llm() -> BaseLLM:
    provider = settings.llm_provider
    if provider == "claude":
        from aain.llm.claude import ClaudeAdapter
        return ClaudeAdapter()
    elif provider == "openai":
        from aain.llm.openai import OpenAIAdapter
        return OpenAIAdapter()
    return MockLLM()


@dataclass
class SystemContext:
    registry: AgentRegistry
    event_bus: AsyncEventBus
    pipeline: DecisionPipeline
    reward_calculator: RewardCalculator
    token_ledger: TokenLedger
    budget_manager: BudgetManager
    internal_auction: InternalAuction
    llm: BaseLLM

    async def shutdown(self) -> None:
        for cluster in self.registry.all_clusters():
            await cluster.stop()


async def bootstrap_system() -> SystemContext:
    setup_logging()

    event_bus = AsyncEventBus(
        max_history=settings.event_bus_max_history,
        handler_timeout_s=settings.event_bus_handler_timeout_ms / 1000.0,
    )
    registry = AgentRegistry()
    llm = get_llm()

    reward_calculator = RewardCalculator(weights={
        "alpha": settings.reward_alpha,
        "beta": settings.reward_beta,
        "gamma": settings.reward_gamma,
        "delta": settings.reward_delta,
        "epsilon": settings.reward_epsilon,
    })

    token_ledger = TokenLedger(initial_mint_per_agent=settings.initial_mint_per_agent)
    budget_manager = BudgetManager(token_ledger, base_budget=settings.economy_base_budget)
    internal_auction = InternalAuction(token_ledger)

    # Create all 7 cluster supervisors
    clusters = [
        IntentClusterSupervisor(event_bus, llm),
        PolicyClusterSupervisor(event_bus),
        AdvertiserClusterSupervisor(event_bus),
        EconomicClusterSupervisor(event_bus),
        CreativeClusterSupervisor(event_bus, llm),
        PlacementClusterSupervisor(event_bus, llm),
        LearningClusterSupervisor(event_bus),
    ]

    for cluster in clusters:
        registry.register_cluster(cluster)
        for agent in cluster.agents:
            registry.register(agent)
            token_ledger.create_account(agent.agent_id)
        await cluster.start()

    pipeline = DecisionPipeline(registry, event_bus, reward_calculator)

    log.info(
        "system_booted",
        agents=registry.agent_count,
        clusters=len(clusters),
        llm_provider=settings.llm_provider,
    )

    return SystemContext(
        registry=registry,
        event_bus=event_bus,
        pipeline=pipeline,
        reward_calculator=reward_calculator,
        token_ledger=token_ledger,
        budget_manager=budget_manager,
        internal_auction=internal_auction,
        llm=llm,
    )


def cli() -> None:
    import uvicorn
    setup_logging()
    uvicorn.run(
        "aain.app:create_app",
        factory=True,
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )


if __name__ == "__main__":
    cli()
