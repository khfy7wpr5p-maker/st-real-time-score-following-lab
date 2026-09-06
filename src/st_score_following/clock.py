from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from math import isfinite
from time import monotonic


@dataclass(frozen=True, slots=True)
class LatencySample:
    input_timestamp_s: float
    output_timestamp_s: float

    def __post_init__(self) -> None:
        if not isfinite(self.input_timestamp_s) or not isfinite(self.output_timestamp_s):
            raise ValueError("latency timestamps must be finite")
        if self.input_timestamp_s < 0 or self.output_timestamp_s < 0:
            raise ValueError("latency timestamps must be >= 0")
        if self.output_timestamp_s < self.input_timestamp_s:
            raise ValueError("output timestamp cannot precede input timestamp")

    @property
    def latency_s(self) -> float:
        return self.output_timestamp_s - self.input_timestamp_s


@dataclass(frozen=True, slots=True)
class LatencySummary:
    count: int
    mean_s: float
    p95_s: float
    max_s: float


def summarize_latency_s(samples: Iterable[float]) -> LatencySummary:
    values = sorted(float(value) for value in samples)
    if not values:
        return LatencySummary(count=0, mean_s=0.0, p95_s=0.0, max_s=0.0)
    if any(not isfinite(value) or value < 0 for value in values):
        raise ValueError("latency samples must be finite and >= 0")

    if len(values) == 1:
        p95 = values[0]
    else:
        position = 0.95 * (len(values) - 1)
        lower = int(position)
        upper = min(lower + 1, len(values) - 1)
        fraction = position - lower
        p95 = values[lower] + (values[upper] - values[lower]) * fraction

    return LatencySummary(
        count=len(values),
        mean_s=sum(values) / len(values),
        p95_s=p95,
        max_s=values[-1],
    )


class StreamClock:
    """Monotonic stream-relative clock with an injectable time source for tests."""

    def __init__(self, time_source: Callable[[], float] = monotonic) -> None:
        self._time_source = time_source
        self._origin = time_source()
        if not isfinite(self._origin):
            raise ValueError("clock origin must be finite")

    def now_s(self) -> float:
        current = self._time_source()
        if not isfinite(current):
            raise ValueError("clock sample must be finite")
        elapsed = current - self._origin
        if elapsed < 0:
            raise RuntimeError("stream clock moved backwards")
        return elapsed
