from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter()


@router.get("/balances")
async def get_balances(request: Request) -> dict:
    system = request.app.state.system
    return system.token_ledger.all_balances()


@router.get("/transactions")
async def get_transactions(request: Request, limit: int = 100) -> list[dict]:
    system = request.app.state.system
    return system.token_ledger.recent_transactions(limit)


@router.get("/budgets")
async def get_budgets(request: Request) -> dict:
    system = request.app.state.system
    allocs = system.budget_manager.get_allocations()
    return {k: v.model_dump() for k, v in allocs.items()}


class MintRequest(BaseModel):
    agent_id: str
    amount: float


@router.post("/mint")
async def mint_tokens(body: MintRequest, request: Request) -> dict:
    system = request.app.state.system
    system.token_ledger.reward(body.agent_id, body.amount)
    return {
        "agent_id": body.agent_id,
        "new_balance": system.token_ledger.balance(body.agent_id),
    }
