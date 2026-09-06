"""Core contracts for ST Real-Time Score Following Lab."""

from .clock import LatencySample, LatencySummary, StreamClock, summarize_latency_s
from .contracts import (
    AlignmentV1,
    ConfidenceV1,
    ObservationKind,
    ObservationV1,
    PerformanceEventV1,
    ScorePositionV1,
    TempoStateV1,
)

__all__ = [
    "AlignmentV1",
    "ConfidenceV1",
    "LatencySample",
    "LatencySummary",
    "ObservationKind",
    "ObservationV1",
    "PerformanceEventV1",
    "ScorePositionV1",
    "StreamClock",
    "TempoStateV1",
    "summarize_latency_s",
]
