from __future__ import annotations

from aain.economy.token_ledger import TokenLedger
from aain.models.economy import BudgetAllocation


class BudgetManager:
    """Allocates computation budgets to agents based on performance.

    High-performing agents get larger budgets (more pipeline invocations).
    """

    def __init__(self, ledger: TokenLedger, base_budget: float = 10.0):
        self.ledger = ledger
        self._allocations: dict[str, BudgetAllocation] = {}
        self.base_budget = base_budget

    def allocate_period(self, agent_ids: list[str]) -> None:
        total_balance = sum(self.ledger.balance(a) for a in agent_ids)
        if total_balance == 0:
            total_balance = 1.0

        for agent_id in agent_ids:
            share = self.ledger.balance(agent_id) / total_balance
            allocation = self.base_budget * (0.5 + share)
            self._allocations[agent_id] = BudgetAllocation(
                agent_id=agent_id,
                cluster_id="",
                allocated_tokens=allocation,
            )

    def can_execute(self, agent_id: str) -> bool:
        alloc = self._allocations.get(agent_id)
        if not alloc:
            return True
        return alloc.spent_tokens < alloc.allocated_tokens

    def record_execution(self, agent_id: str, cost: float = 1.0) -> None:
        if agent_id in self._allocations:
            self._allocations[agent_id].spent_tokens += cost

    def get_allocations(self) -> dict[str, BudgetAllocation]:
        return dict(self._allocations)
