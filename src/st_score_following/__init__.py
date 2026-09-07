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
from .error_intelligence import (
    AbstentionKind,
    EvidenceAbstentionV1,
    EvidenceKind,
    EvidenceOrigin,
    PerformanceErrorIntelligenceReportV1,
    PerformanceErrorIntelligenceSummaryV1,
    PerformanceEvidenceEventV1,
    build_performance_error_intelligence_report,
)
from .integrations import StradiCsvOutputAdapter
from .performance_alignment import (
    AlignmentProvenanceV1,
    PerformanceAlignmentPointV1,
    PerformanceAlignmentReportV1,
    PerformanceAlignmentSummaryV1,
    SegmentBoundaryReason,
    TimingClass,
    build_performance_alignment_report,
)
from .recovery import RecoveryAwareSymbolicFollower, RecoveryMatch
from .symbolic import CausalSymbolicFollower, SymbolicScoreEvent
from .transcription import TranscriptionAdapter, TranscriptionRunResult

__all__ = [
    "AbstentionKind",
    "AlignmentProvenanceV1",
    "AlignmentV1",
    "CausalSymbolicFollower",
    "ConfidenceV1",
    "EvidenceAbstentionV1",
    "EvidenceKind",
    "EvidenceOrigin",
    "LatencySample",
    "LatencySummary",
    "ObservationKind",
    "ObservationV1",
    "PerformanceAlignmentPointV1",
    "PerformanceAlignmentReportV1",
    "PerformanceAlignmentSummaryV1",
    "PerformanceErrorIntelligenceReportV1",
    "PerformanceErrorIntelligenceSummaryV1",
    "PerformanceEvidenceEventV1",
    "PerformanceEventV1",
    "RecoveryAwareSymbolicFollower",
    "RecoveryMatch",
    "ScorePositionV1",
    "SegmentBoundaryReason",
    "StradiCsvOutputAdapter",
    "StreamClock",
    "SymbolicScoreEvent",
    "TempoStateV1",
    "TimingClass",
    "TranscriptionAdapter",
    "TranscriptionRunResult",
    "build_performance_alignment_report",
    "build_performance_error_intelligence_report",
    "summarize_latency_s",
]
