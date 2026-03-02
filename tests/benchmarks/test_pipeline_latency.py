from __future__ import annotations

import pytest

from aain.main import bootstrap_system


async def test_pipeline_p95_under_300ms() -> None:
    """Run 100 pipeline executions and assert p95 < 300ms."""
    system = await bootstrap_system()
    latencies: list[float] = []

    queries = [
        "best CRM for startups",
        "compare project management tools",
        "how to build an online store",
        "top cloud computing providers",
        "affordable email marketing software",
    ]

    for i in range(100):
        query = queries[i % len(queries)]
        result = await system.pipeline.execute({
            "query": query,
            "session_id": f"bench_{i}",
            "user_id": "bench_user",
        })
        if "total_latency_ms" in result:
            latencies.append(result["total_latency_ms"])

    await system.shutdown()

    assert len(latencies) > 0, "No latency measurements collected"

    latencies.sort()
    p50 = latencies[len(latencies) // 2]
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]

    print(f"\n  Pipeline Latency Benchmark (n={len(latencies)}):")
    print(f"    p50: {p50:.2f}ms")
    print(f"    p95: {p95:.2f}ms")
    print(f"    p99: {p99:.2f}ms")

    assert p50 < 200, f"p50 latency {p50:.2f}ms exceeds 200ms"
    assert p95 < 300, f"p95 latency {p95:.2f}ms exceeds 300ms"
    assert p99 < 500, f"p99 latency {p99:.2f}ms exceeds 500ms"


async def test_pipeline_throughput() -> None:
    """Measure pipeline throughput (decisions/second)."""
    system = await bootstrap_system()
    import time

    start = time.monotonic()
    count = 50

    for i in range(count):
        await system.pipeline.execute({
            "query": "best CRM",
            "session_id": f"throughput_{i}",
            "user_id": "bench",
        })

    elapsed = time.monotonic() - start
    throughput = count / elapsed

    await system.shutdown()

    print(f"\n  Pipeline Throughput: {throughput:.0f} decisions/sec ({count} in {elapsed:.2f}s)")
    assert throughput > 10, f"Throughput {throughput:.0f}/s below minimum 10/s"
