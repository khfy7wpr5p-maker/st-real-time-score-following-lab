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
from .integrations import StradiCsvOutputAdapter
from .symbolic import CausalSymbolicFollower, SymbolicScoreEvent
from .transcription import TranscriptionAdapter, TranscriptionRunResult

__all__ = [
    "AlignmentV1",
    "CausalSymbolicFollower",
    "ConfidenceV1",
    "LatencySample",
    "LatencySummary",
    "ObservationKind",
    "ObservationV1",
    "PerformanceEventV1",
    "ScorePositionV1",
    "StradiCsvOutputAdapter",
    "StreamClock",
    "SymbolicScoreEvent",
    "TempoStateV1",
    "TranscriptionAdapter",
    "TranscriptionRunResult",
    "summarize_latency_s",
]
