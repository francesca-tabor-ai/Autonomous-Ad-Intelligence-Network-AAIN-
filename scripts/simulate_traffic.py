#!/usr/bin/env python3
"""Simulate realistic ad traffic through the AAIN pipeline.

Usage:
    python scripts/simulate_traffic.py
    python scripts/simulate_traffic.py --queries 500 --concurrency 10
"""

from __future__ import annotations

import argparse
import asyncio
import random
import time

SAMPLE_QUERIES = [
    "What's the best CRM for startups?",
    "compare Salesforce vs HubSpot",
    "how to build an online store",
    "top cloud computing services",
    "best project management software",
    "affordable email marketing tools",
    "how to learn Python programming",
    "best accounting software for small business",
    "compare AWS vs Azure vs GCP",
    "top SEO tools for agencies",
    "best HR software for remote teams",
    "cheap web hosting providers",
    "how does machine learning work",
    "best video editing software",
    "top cybersecurity tools for enterprises",
    "what is the weather today",
    "how to cook pasta",
    "best running shoes 2024",
    "online course platforms comparison",
    "free CRM for freelancers",
]

SESSION_IDS = [f"sim_session_{i}" for i in range(50)]
USER_IDS = [f"sim_user_{i}" for i in range(20)]


async def run_simulation(total_queries: int, concurrency: int) -> None:
    from aain.main import bootstrap_system

    system = await bootstrap_system()

    print(f"\n{'='*60}")
    print(f"  AAIN Traffic Simulation")
    print(f"  Queries: {total_queries}  |  Concurrency: {concurrency}")
    print(f"  Agents: {system.registry.agent_count}  |  Clusters: {len(system.registry.all_clusters())}")
    print(f"{'='*60}\n")

    latencies: list[float] = []
    ad_served = 0
    no_ad = 0
    errors = 0
    start = time.monotonic()

    sem = asyncio.Semaphore(concurrency)

    async def run_one(i: int) -> None:
        nonlocal ad_served, no_ad, errors
        async with sem:
            try:
                result = await system.pipeline.execute({
                    "query": random.choice(SAMPLE_QUERIES),
                    "session_id": random.choice(SESSION_IDS),
                    "user_id": random.choice(USER_IDS),
                })
                if "total_latency_ms" in result:
                    latencies.append(result["total_latency_ms"])
                if result.get("decision"):
                    ad_served += 1
                else:
                    no_ad += 1
            except Exception:
                errors += 1

    tasks = [run_one(i) for i in range(total_queries)]
    await asyncio.gather(*tasks)

    elapsed = time.monotonic() - start

    # Stats
    latencies.sort()
    p50 = latencies[len(latencies) // 2] if latencies else 0
    p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0
    p99 = latencies[int(len(latencies) * 0.99)] if latencies else 0
    throughput = total_queries / elapsed if elapsed > 0 else 0

    print(f"  --- Results ---")
    print(f"  Total queries:   {total_queries}")
    print(f"  Ads served:      {ad_served} ({ad_served/total_queries*100:.1f}%)")
    print(f"  No ad (vetoed):  {no_ad} ({no_ad/total_queries*100:.1f}%)")
    print(f"  Errors:          {errors}")
    print(f"")
    print(f"  --- Latency ---")
    print(f"  p50:  {p50:.2f}ms")
    print(f"  p95:  {p95:.2f}ms")
    print(f"  p99:  {p99:.2f}ms")
    print(f"")
    print(f"  --- Throughput ---")
    print(f"  {throughput:.0f} decisions/sec")
    print(f"  Total time: {elapsed:.2f}s")
    print(f"")

    # Economy snapshot
    balances = system.token_ledger.all_balances()
    top_agents = sorted(balances.items(), key=lambda x: x[1], reverse=True)[:5]
    print(f"  --- Top Agents (by token balance) ---")
    for agent_id, balance in top_agents:
        print(f"  {agent_id:>30}: {balance:.1f} tokens")

    print(f"\n{'='*60}\n")

    await asyncio.sleep(0.1)
    await system.shutdown()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AAIN Traffic Simulator")
    parser.add_argument("--queries", type=int, default=200, help="Number of queries")
    parser.add_argument("--concurrency", type=int, default=5, help="Concurrent pipeline executions")
    args = parser.parse_args()

    asyncio.run(run_simulation(args.queries, args.concurrency))
