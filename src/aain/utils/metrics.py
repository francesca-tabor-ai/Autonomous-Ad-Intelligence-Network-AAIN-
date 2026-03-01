from __future__ import annotations

import time
from dataclasses import dataclass, field


@dataclass
class LatencyTracker:
    samples: list[float] = field(default_factory=list)
    max_samples: int = 1000

    def record(self, ms: float) -> None:
        self.samples.append(ms)
        if len(self.samples) > self.max_samples:
            self.samples = self.samples[-self.max_samples:]

    @property
    def p50(self) -> float:
        if not self.samples:
            return 0.0
        s = sorted(self.samples)
        return s[len(s) // 2]

    @property
    def p95(self) -> float:
        if not self.samples:
            return 0.0
        s = sorted(self.samples)
        return s[int(len(s) * 0.95)]

    @property
    def p99(self) -> float:
        if not self.samples:
            return 0.0
        s = sorted(self.samples)
        return s[int(len(s) * 0.99)]

    def summary(self) -> dict:
        return {
            "count": len(self.samples),
            "p50_ms": round(self.p50, 2),
            "p95_ms": round(self.p95, 2),
            "p99_ms": round(self.p99, 2),
        }


class Timer:
    def __init__(self) -> None:
        self._start: float = 0.0
        self._elapsed_ms: float = 0.0

    def __enter__(self) -> "Timer":
        self._start = time.monotonic()
        return self

    def __exit__(self, *args: object) -> None:
        self._elapsed_ms = (time.monotonic() - self._start) * 1000

    @property
    def elapsed_ms(self) -> float:
        return self._elapsed_ms
