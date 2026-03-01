from __future__ import annotations

import time


class TokenLedger:
    """Central ledger for the internal agent economy.

    Agents earn tokens for successful pipeline contributions.
    Agents spend tokens to bid for processing priority.
    """

    def __init__(self, initial_mint_per_agent: float = 100.0):
        self._balances: dict[str, float] = {}
        self._transaction_log: list[dict] = []
        self.initial_mint = initial_mint_per_agent

    def create_account(self, agent_id: str) -> None:
        self._balances[agent_id] = self.initial_mint
        self._log("mint", "system", agent_id, self.initial_mint)

    def balance(self, agent_id: str) -> float:
        return self._balances.get(agent_id, 0.0)

    def all_balances(self) -> dict[str, float]:
        return dict(self._balances)

    def transfer(self, from_id: str, to_id: str, amount: float) -> bool:
        if self._balances.get(from_id, 0) < amount:
            return False
        self._balances[from_id] -= amount
        self._balances[to_id] = self._balances.get(to_id, 0) + amount
        self._log("transfer", from_id, to_id, amount)
        return True

    def reward(self, agent_id: str, amount: float) -> None:
        self._balances[agent_id] = self._balances.get(agent_id, 0) + amount
        self._log("reward", "system", agent_id, amount)

    def deduct(self, agent_id: str, amount: float) -> bool:
        if self._balances.get(agent_id, 0) < amount:
            return False
        self._balances[agent_id] -= amount
        self._log("deduct", agent_id, "system", amount)
        return True

    def _log(self, tx_type: str, from_id: str, to_id: str, amount: float) -> None:
        self._transaction_log.append({
            "type": tx_type,
            "from": from_id,
            "to": to_id,
            "amount": amount,
            "timestamp": time.time(),
        })

    @property
    def transactions(self) -> list[dict]:
        return list(self._transaction_log)

    def recent_transactions(self, limit: int = 100) -> list[dict]:
        return self._transaction_log[-limit:]
