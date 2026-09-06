"""Core contracts for ST Real-Time Score Following Lab."""

from .clock import LatencySample, StreamClock
from .contracts import (
    AlignmentV1,
    ConfidenceV1,
    ObservationKind,
    ObservationV1,
    PerformanceEventV1,
    ScorePositionV1,
    TempoStateV1,
)
from .symbolic import CausalSymbolicFollower, SymbolicScoreEvent
from .transcription import TranscriptionAdapter, TranscriptionRunResult

__all__ = [
    "AlignmentV1",
    "CausalSymbolicFollower",
    "ConfidenceV1",
    "LatencySample",
    "ObservationKind",
    "ObservationV1",
    "PerformanceEventV1",
    "ScorePositionV1",
    "StreamClock",
    "SymbolicScoreEvent",
    "TempoStateV1",
    "TranscriptionAdapter",
    "TranscriptionRunResult",
]
