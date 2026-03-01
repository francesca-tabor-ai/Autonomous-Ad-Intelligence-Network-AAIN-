from __future__ import annotations

import pytest

from aain.economy.token_ledger import TokenLedger
from aain.economy.budget_manager import BudgetManager
from aain.economy.internal_auction import InternalAuction
from aain.economy.reward_calculator import RewardCalculator
from aain.core.blackboard import Blackboard
from aain.models.intent import UserState


def test_ledger_create_account() -> None:
    ledger = TokenLedger(initial_mint_per_agent=100.0)
    ledger.create_account("agent_1")
    assert ledger.balance("agent_1") == 100.0


def test_ledger_transfer() -> None:
    ledger = TokenLedger(initial_mint_per_agent=100.0)
    ledger.create_account("a")
    ledger.create_account("b")
    assert ledger.transfer("a", "b", 30.0)
    assert ledger.balance("a") == 70.0
    assert ledger.balance("b") == 130.0


def test_ledger_insufficient_balance() -> None:
    ledger = TokenLedger(initial_mint_per_agent=10.0)
    ledger.create_account("a")
    assert not ledger.transfer("a", "b", 20.0)


def test_ledger_reward_and_deduct() -> None:
    ledger = TokenLedger(initial_mint_per_agent=50.0)
    ledger.create_account("a")
    ledger.reward("a", 25.0)
    assert ledger.balance("a") == 75.0
    assert ledger.deduct("a", 10.0)
    assert ledger.balance("a") == 65.0


def test_budget_manager() -> None:
    ledger = TokenLedger(initial_mint_per_agent=100.0)
    ledger.create_account("a")
    ledger.create_account("b")
    ledger.reward("a", 100.0)  # a has 200, b has 100

    bm = BudgetManager(ledger, base_budget=10.0)
    bm.allocate_period(["a", "b"])
    assert bm.can_execute("a")
    assert bm.can_execute("b")


async def test_internal_auction() -> None:
    ledger = TokenLedger(initial_mint_per_agent=100.0)
    ledger.create_account("a")
    ledger.create_account("b")
    ledger.create_account("c")

    auction = InternalAuction(ledger)
    result = await auction.run_auction("task_1", [("a", 10.0), ("b", 15.0), ("c", 8.0)])
    assert result is not None
    winner_id, clearing_price = result
    assert winner_id == "b"
    assert clearing_price == 10.0  # Second price


def test_reward_calculator() -> None:
    bb = Blackboard("test")
    bb.write("test", "final_price", 5.0)
    bb.write("test", "user_state", UserState(
        session_id="s1", engagement_level=0.7, ad_fatigue_score=0.2,
    ))
    bb.write("test", "estimated_roas", 3.0)

    calc = RewardCalculator()
    reward = calc.calculate(bb)
    assert reward.total > 0
    assert reward.revenue_component == 5.0
    assert reward.engagement_component == 0.7
