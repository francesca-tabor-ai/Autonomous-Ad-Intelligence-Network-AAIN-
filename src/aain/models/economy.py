from __future__ import annotations

from pydantic import BaseModel


class TokenBalance(BaseModel):
    agent_id: str
    balance: float = 0.0
    total_earned: float = 0.0
    total_spent: float = 0.0


class BudgetAllocation(BaseModel):
    agent_id: str
    cluster_id: str
    allocated_tokens: float
    spent_tokens: float = 0.0
    period: str = "hourly"


class BidRecord(BaseModel):
    bidder_agent_id: str
    task_id: str
    bid_amount: float
    outcome: str = "pending"
    timestamp: float = 0.0
