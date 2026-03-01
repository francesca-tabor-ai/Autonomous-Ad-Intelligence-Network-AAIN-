# AAIN — Autonomous Ad Intelligence Network

A multi-agent ad decision system that uses 7 specialized agent clusters (21 agents) coordinated by a Strategic Supervisor to make real-time advertising decisions. Built with Python, asyncio, and a custom blackboard + event bus architecture.

## Architecture

```
User Intent Stream
       ↓
┌──────────────────────────────────────────────────┐
│              Strategic Supervisor                 │
├──────────────────────────────────────────────────┤
│                                                  │
│  1. Intent Intelligence    ──→  Parse intent,    │
│     ├─ Intent Parser            score commercial │
│     ├─ Commercial Relevance     likelihood,      │
│     └─ User State               track session    │
│                                                  │
│  2. Policy & Ethics        ──→  Compliance gate, │
│     ├─ Compliance               brand safety,    │
│     ├─ Brand Safety             trust guardian    │
│     └─ Trust Guardian           (can VETO)       │
│                                                  │
│  3. Advertiser Strategy    ──→  Select campaigns,│
│     ├─ Campaign Optimizer       compute bids,    │
│     ├─ Bid Strategy             expand audiences │
│     └─ Audience Expansion                        │
│                                                  │
│  4. Economic Optimization  ──→  Run auction,     │
│     ├─ Revenue Maximization     set pricing,     │
│     ├─ Pricing Model            predict LTV      │
│     └─ LTV Prediction                            │
│                                                  │
│  5. Creative Intelligence  ──→  Generate copy,   │
│     ├─ Dynamic Creative         select assets,   │
│     ├─ Asset Selection          A/B test         │
│     └─ Variant Testing                           │
│                                                  │
│  6. Placement Orchestration──→  Pick surface,    │
│     ├─ Surface Allocation       insert naturally │
│     └─ Conversational Insertion                  │
│                                                  │
│  7. Learning & Governance  ──→  RL updates,      │
│     ├─ RL Controller            drift detection  │
│     └─ Drift Detection          (runs async)     │
│                                                  │
├──────────────────────────────────────────────────┤
│  Event Bus  │  Blackboard  │  Internal Economy   │
└──────────────────────────────────────────────────┘
       ↓
  Ad Decision (< 300ms target)
```

## Decision Flow

```
Time (ms)  0    40    70      120    160     210    250        300
           |-----|-----|--------|------|-------|------||.........|
           Intent Policy Advertiser Economic Creative Placement  Learning
             40    30      50       40     50     40     (async)
                    ^
                    Gate: can veto
           |<------------- synchronous (250ms) ---------->|<-async->|
```

**Example**: User asks *"What's the best CRM for startups?"*

1. **Intent Parser** → Commercial Investigation / Consideration stage
2. **Commercial Relevance** → 0.82 monetization score
3. **Policy** → Passes compliance, brand safety, trust checks
4. **Campaign Optimizer** → Matches CRM campaigns (Salesforce, HubSpot, AWS)
5. **Bid Strategy** → Computes optimal bids per campaign
6. **Revenue Max** → Second-price auction, winner pays clearing price
7. **Creative Generator** → Tailors message to startup audience
8. **Placement** → Conversational inline surface
9. **RL Controller** → Updates reward weights (async)

## Reward Function

```
Global Reward = α × Revenue
              + β × Engagement
              + γ × Retention
              + δ × Advertiser ROAS
              - ε × Trust Erosion
```

Weights (α=0.3, β=0.25, γ=0.2, δ=0.15, ε=0.1) are dynamically adjusted by the RL Controller.

## Internal Agent Economy

Agents participate in a tokenized internal economy:

- **Token Ledger** — Each agent has a balance; tokens are minted as rewards for successful pipeline contributions
- **Budget Manager** — High-performing agents receive larger computation budgets
- **Internal Auction** — When multiple agents compete for a task, they bid tokens (second-price)
- **Agent P&L** — Every agent's performance is tracked via token balance

## Quick Start

```bash
# Clone and setup
git clone https://github.com/francesca-tabor-ai/Autonomous-Ad-Intelligence-Network-AAIN-.git
cd Autonomous-Ad-Intelligence-Network-AAIN-

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install
pip install -e ".[dev]"

# Run the demo pipeline
python scripts/run_pipeline.py

# Run with a custom query
python scripts/run_pipeline.py "compare Salesforce vs HubSpot"

# Run tests
pytest tests/ -v

# Start the API server
make run
# → http://localhost:8000/docs for OpenAPI dashboard
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/health` | GET | System health and uptime |
| `/api/v1/ready` | GET | Readiness check |
| `/api/v1/agents` | GET | List all agents with metrics |
| `/api/v1/agents/{id}` | GET | Single agent detail |
| `/api/v1/agents/{id}/pause` | POST | Pause an agent (human override) |
| `/api/v1/agents/{id}/resume` | POST | Resume a paused agent |
| `/api/v1/pipeline/execute` | POST | Run a pipeline decision |
| `/api/v1/pipeline/stats` | GET | Latency statistics |
| `/api/v1/events` | GET | Event bus history |
| `/api/v1/economy/balances` | GET | Agent token balances |
| `/api/v1/economy/transactions` | GET | Token transaction log |
| `/api/v1/oversight/audit-log` | GET | Regulatory audit log |
| `/api/v1/oversight/override` | POST | Human override command |
| `/api/v1/oversight/reward-weights` | GET/POST | View or update reward weights |
| `/api/v1/ws/events` | WebSocket | Live event stream |

### Example: Execute Pipeline

```bash
curl -X POST http://localhost:8000/api/v1/pipeline/execute \
  -H "Content-Type: application/json" \
  -d '{"query": "best project management tools", "session_id": "s1", "user_id": "u1"}'
```

## Project Structure

```
src/aain/
├── core/           # Event bus, blackboard, base agent, pipeline, registry
├── models/         # Pydantic domain models (intent, auction, campaign, etc.)
├── llm/            # Pluggable LLM layer (mock, Claude, OpenAI)
├── clusters/       # 7 agent clusters with 21 specialist agents
│   ├── intent/         advertiser/       creative/
│   ├── economic/       placement/        policy/
│   └── learning/
├── economy/        # Token ledger, budget manager, internal auction, rewards
├── api/            # FastAPI dashboard and oversight endpoints
├── storage/        # Persistence abstraction (in-memory, Redis)
└── utils/          # Logging, metrics, ID generation
```

## Configuration

Environment variables (or `.env` file):

| Variable | Default | Description |
|----------|---------|-------------|
| `AAIN_LOG_LEVEL` | `INFO` | Logging level |
| `AAIN_LLM_PROVIDER` | `mock` | LLM provider: `mock`, `claude`, `openai` |
| `AAIN_API_PORT` | `8000` | API server port |
| `AAIN_REWARD_ALPHA` | `0.3` | Revenue weight in reward function |
| `AAIN_REWARD_BETA` | `0.25` | Engagement weight |
| `AAIN_REWARD_GAMMA` | `0.2` | Retention weight |
| `AAIN_REWARD_DELTA` | `0.15` | Advertiser ROAS weight |
| `AAIN_REWARD_EPSILON` | `0.1` | Trust erosion penalty weight |
| `ANTHROPIC_API_KEY` | — | Required when `LLM_PROVIDER=claude` |
| `OPENAI_API_KEY` | — | Required when `LLM_PROVIDER=openai` |

## Scaling Roadmap

| Phase | Description |
|-------|-------------|
| **Phase 1** (current) | Rule-based + ML assist. All agents functional with mock LLM. |
| **Phase 2** | Multi-agent bidding autonomy. Real LLM integration, trained bid models. |
| **Phase 3** | Fully RL-coordinated monetization. PPO/A2C training for reward optimization. |
| **Phase 4** | Cross-platform intent arbitrage. Distributed deployment with Redis event bus. |

## Tech Stack

- **Python 3.11+** with **asyncio** for async-first architecture
- **Pydantic v2** for domain models and validation
- **FastAPI** for the dashboard API
- **structlog** for structured logging with correlation IDs
- **Custom framework** — no LangChain/AutoGen/CrewAI dependency
