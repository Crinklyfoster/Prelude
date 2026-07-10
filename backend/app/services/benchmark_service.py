from __future__ import annotations

import time
from dataclasses import dataclass, asdict


@dataclass(slots=True)
class BenchmarkResult:
    stage: str
    duration_ms: float


class BenchmarkTimer:
    def __init__(self):
        self._starts: dict[str, float] = {}
        self.results: list[BenchmarkResult] = []

    def start(self, stage: str):
        self._starts[stage] = time.perf_counter()

    def stop(self, stage: str):
        start = self._starts.pop(stage)

        self.results.append(
            BenchmarkResult(
                stage=stage,
                duration_ms=(time.perf_counter() - start) * 1000,
            )
        )

    @property
    def total_ms(self):
        return sum(r.duration_ms for r in self.results)

    def as_dict(self):
        return {
            "total_ms": round(self.total_ms, 2),
            "stages": [
                {
                    "stage": r.stage,
                    "duration_ms": round(r.duration_ms, 2),
                }
                for r in self.results
            ],
        }
