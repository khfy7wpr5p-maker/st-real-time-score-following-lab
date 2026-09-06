from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from time import monotonic
from typing import Callable


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
