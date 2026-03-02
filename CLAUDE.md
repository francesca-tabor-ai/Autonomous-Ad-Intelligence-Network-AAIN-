# AAIN — Autonomous Ad Intelligence Network

## Project Overview
Multi-agent ad decision system: 7 agent clusters (21 specialist agents) coordinated by a Strategic Supervisor. Python, asyncio, custom framework — no LangChain/AutoGen.

## Architecture
- **Event Bus** (`core/event_bus.py`): Async pub/sub, ring-buffer history, 100ms handler timeout
- **Blackboard** (`core/blackboard.py`): Shared context per pipeline run, audit trail
- **Pipeline** (`core/pipeline.py`): 6 sync stages + 1 async tail, 300ms total budget
- **Agents** (`core/agent.py`): BaseAgent ABC → ClusterSupervisor → StrategicSupervisor hierarchy
- **Economy** (`economy/`): Token ledger, budget manager, second-price internal auction

## Pipeline Order
Intent (40ms) → Policy/gate (30ms) → Advertiser (50ms) → Economic (40ms) → Creative (50ms) → Placement (40ms) → Learning (async 50ms)

## Key Commands
```bash
source .venv/bin/activate
pytest tests/ -v                          # Run all tests
python scripts/run_pipeline.py            # Demo
python scripts/simulate_traffic.py        # Load test
make run                                  # API server at :8000
```

## Code Layout
- `src/aain/core/` — Framework primitives (event bus, blackboard, agent, pipeline, registry)
- `src/aain/models/` — Pydantic domain models
- `src/aain/clusters/` — 7 agent clusters (intent, policy, advertiser, economic, creative, placement, learning)
- `src/aain/economy/` — Internal agent economy (tokens, budgets, auctions, rewards)
- `src/aain/llm/` — Pluggable LLM layer (mock, claude, openai adapters)
- `src/aain/api/` — FastAPI dashboard endpoints
- `tests/` — unit, cluster, integration, benchmarks

## Conventions
- Async-first: all agent processing uses `async def process()`
- Pydantic v2 for all data models
- Event types defined in `core/types.py`
- Each cluster has a `supervisor.py` that wires its agents
- Pipeline context stored via `PipelineContext` class dict keyed by correlation_id
- Tests use `pytest-asyncio` with `asyncio_mode = "auto"`
