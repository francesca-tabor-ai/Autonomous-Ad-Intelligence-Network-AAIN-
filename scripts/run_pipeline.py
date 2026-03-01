#!/usr/bin/env python3
"""Demo: Run the AAIN pipeline with a sample query.

Usage:
    python scripts/run_pipeline.py
    python scripts/run_pipeline.py "compare Salesforce vs HubSpot"
"""

from __future__ import annotations

import asyncio
import json
import sys


async def main(query: str = "What's the best CRM for startups?") -> None:
    from aain.main import bootstrap_system

    print(f"\n{'='*60}")
    print(f"  AAIN Pipeline Demo")
    print(f"{'='*60}")
    print(f"\n  Query: {query}\n")

    system = await bootstrap_system()
    print(f"  System booted: {system.registry.agent_count} agents across "
          f"{len(system.registry.all_clusters())} clusters\n")

    result = await system.pipeline.execute({
        "query": query,
        "session_id": "demo_session",
        "user_id": "demo_user",
    })

    print(f"  Correlation ID: {result['correlation_id']}")

    if result.get("decision"):
        print(f"\n  --- Ad Decision ---")
        decision = result["decision"]
        print(f"  Surface: {decision.get('surface', {}).get('surface_type', 'N/A')}")
        print(f"  Position: {decision.get('position', 'N/A')}")

        creative = result.get("creative", {})
        if creative:
            print(f"\n  --- Creative ---")
            print(f"  Headline: {creative.get('headline', 'N/A')}")
            print(f"  Body: {creative.get('body', 'N/A')}")
            print(f"  CTA: {creative.get('cta_text', 'N/A')}")
            print(f"  Test Group: {creative.get('test_group', 'N/A')}")

        print(f"\n  --- Economics ---")
        print(f"  Price: ${result.get('pricing', 0):.4f}")
        print(f"  Pricing Model: {result.get('pricing_model', 'N/A')}")

        auction = result.get("auction_result", {})
        if auction:
            print(f"  Auction Winner: {auction.get('winner_campaign_id', 'N/A')}")
            print(f"  Clearing Price: ${auction.get('clearing_price', 0):.4f}")
            print(f"  Participants: {auction.get('participants', 0)}")
    else:
        print(f"\n  No ad served. Reason: {result.get('reason', 'unknown')}")

    if "stage_timings" in result:
        print(f"\n  --- Stage Timings ---")
        for stage, ms in result["stage_timings"].items():
            bar = "█" * int(ms / 2)
            print(f"  {stage:>15}: {ms:6.1f}ms {bar}")
        print(f"  {'TOTAL':>15}: {result.get('total_latency_ms', 0):6.1f}ms")

    print(f"\n{'='*60}\n")

    # Wait for async tail (learning cluster)
    await asyncio.sleep(0.1)
    await system.shutdown()


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "What's the best CRM for startups?"
    asyncio.run(main(query))
