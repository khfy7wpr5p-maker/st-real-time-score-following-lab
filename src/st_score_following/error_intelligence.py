from __future__ import annotations

import csv
import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from io import StringIO
from math import isfinite
from statistics import mean
from typing import Any

from .contracts import ConfidenceV1
from .followers.base import FollowerRunResult
from .performance_alignment import (
    PerformanceAlignmentReportV1,
    SegmentBoundaryReason,
    TimingClass,
)


class EvidenceKind(StrEnum):
    TIMING_EARLY = "timing_early"
    TIMING_LATE = "timing_late"
    UNMATCHED_OBSERVATION = "unmatched_observation"
    SKIPPED_SCORE_REGION = "skipped_score_region"
    SCORE_DISCONTINUITY = "score_discontinuity"
    PERFORMANCE_GAP = "performance_gap"


class EvidenceOrigin(StrEnum):
    PERFORMANCE_ALIGNMENT = "performance_alignment"
    RECOVERY_AUDIT = "recovery_audit"


class AbstentionKind(StrEnum):
    PITCH_ERROR_IDENTITY = "pitch_error_identity"
    UNMATCHED_OBSERVATION_SEMANTICS = "unmatched_observation_semantics"
    ARTICULATION = "articulation"
    DYNAMICS = "dynamics"
    MUSICAL_INTENT = "musical_intent"
    PEDAGOGICAL_GRADE = "pedagogical_grade"


@dataclass(frozen=True, slots=True)
class PerformanceEvidenceEventV1:
    evidence_id: str
    kind: EvidenceKind
    origin: EvidenceOrigin
    source_reference: str
    sequence_id: int | None = None
    segment_id: int | None = None
    score_beat: float | None = None
    performance_time_s: float | None = None
    deviation_ms: float | None = None
    score_index_start: int | None = None
    score_index_end: int | None = None
    count: int | None = None
    confidence: ConfidenceV1 | None = None
    schema_version: str = field(default="performance_evidence_event_v1", init=False)

    def __post_init__(self) -> None:
        if not self.evidence_id.strip():
            raise ValueError("evidence_id must be non-empty")
        if not self.source_reference.strip():
            raise ValueError("source_reference must be non-empty")
        if self.sequence_id is not None and self.sequence_id < 0:
            raise ValueError("sequence_id must be >= 0 when present")
        if self.segment_id is not None and self.segment_id < 0:
            raise ValueError("segment_id must be >= 0 when present")
        for name, value in (
            ("score_beat", self.score_beat),
            ("performance_time_s", self.performance_time_s),
        ):
            if value is not None and (not isfinite(value) or value < 0):
                raise ValueError(f"{name} must be finite and >= 0 when present")
        if self.deviation_ms is not None and not isfinite(self.deviation_ms):
            raise ValueError("deviation_ms must be finite when present")
        if self.score_index_start is not None and self.score_index_start < 0:
            raise ValueError("score_index_start must be >= 0 when present")
        if self.score_index_end is not None and self.score_index_end < 0:
            raise ValueError("score_index_end must be >= 0 when present")
        if (
            self.score_index_start is not None
            and self.score_index_end is not None
            and self.score_index_end < self.score_index_start
        ):
            raise ValueError("score_index_end must be >= score_index_start")
        if self.count is not None and self.count < 1:
            raise ValueError("count must be >= 1 when present")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["kind"] = self.kind.value
        data["origin"] = self.origin.value
        return data


@dataclass(frozen=True, slots=True)
class EvidenceAbstentionV1:
    kind: AbstentionKind
    reason: str
    source_reference: str | None = None
    schema_version: str = field(default="evidence_abstention_v1", init=False)

    def __post_init__(self) -> None:
        if not self.reason.strip():
            raise ValueError("reason must be non-empty")
        if self.source_reference is not None and not self.source_reference.strip():
            raise ValueError("source_reference must be non-empty when present")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["kind"] = self.kind.value
        return data


@dataclass(frozen=True, slots=True)
class PerformanceErrorIntelligenceSummaryV1:
    evidence_event_count: int
    counts_by_kind: dict[str, int]
    events_with_confidence: int
    events_without_confidence: int
    abstention_count: int
    timing_event_count: int
    mean_absolute_timing_deviation_ms: float | None
    max_absolute_timing_deviation_ms: float | None
    unmatched_observation_count: int
    skipped_score_event_count: int
    score_discontinuity_events: int
    performance_gap_events: int
    schema_version: str = field(
        default="performance_error_intelligence_summary_v1",
        init=False,
    )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PerformanceErrorIntelligenceReportV1:
    source_alignment_schema: str
    source_recovery_backend: str | None
    events: tuple[PerformanceEvidenceEventV1, ...]
    abstentions: tuple[EvidenceAbstentionV1, ...]
    summary: PerformanceErrorIntelligenceSummaryV1
    authority_boundary: str = field(
        default="research_evidence_not_pedagogical_authority",
        init=False,
    )
    schema_version: str = field(
        default="performance_error_intelligence_report_v1",
        init=False,
    )

    def __post_init__(self) -> None:
        if not self.source_alignment_schema.strip():
            raise ValueError("source_alignment_schema must be non-empty")
        if self.source_recovery_backend is not None and not self.source_recovery_backend.strip():
            raise ValueError("source_recovery_backend must be non-empty when present")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "authority_boundary": self.authority_boundary,
            "source_alignment_schema": self.source_alignment_schema,
            "source_recovery_backend": self.source_recovery_backend,
            "summary": self.summary.to_dict(),
            "events": [event.to_dict() for event in self.events],
            "abstentions": [item.to_dict() for item in self.abstentions],
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True, allow_nan=False)

    def to_csv(self) -> str:
        fieldnames = [
            "evidence_id",
            "kind",
            "origin",
            "source_reference",
            "sequence_id",
            "segment_id",
            "score_beat",
            "performance_time_s",
            "deviation_ms",
            "score_index_start",
            "score_index_end",
            "count",
            "confidence_value",
            "confidence_source",
            "confidence_calibrated",
            "confidence_reason",
        ]
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for event in self.events:
            confidence = event.confidence
            writer.writerow(
                {
                    "evidence_id": event.evidence_id,
                    "kind": event.kind.value,
                    "origin": event.origin.value,
                    "source_reference": event.source_reference,
                    "sequence_id": "" if event.sequence_id is None else event.sequence_id,
                    "segment_id": "" if event.segment_id is None else event.segment_id,
                    "score_beat": "" if event.score_beat is None else event.score_beat,
                    "performance_time_s": (
                        "" if event.performance_time_s is None else event.performance_time_s
                    ),
                    "deviation_ms": "" if event.deviation_ms is None else event.deviation_ms,
                    "score_index_start": (
                        "" if event.score_index_start is None else event.score_index_start
                    ),
                    "score_index_end": (
                        "" if event.score_index_end is None else event.score_index_end
                    ),
                    "count": "" if event.count is None else event.count,
                    "confidence_value": "" if confidence is None else confidence.value,
                    "confidence_source": "" if confidence is None else confidence.source,
                    "confidence_calibrated": (
                        "" if confidence is None else confidence.calibrated
                    ),
                    "confidence_reason": (
                        "" if confidence is None or confidence.reason is None else confidence.reason
                    ),
                }
            )
        return output.getvalue()


def _recovery_matches(result: FollowerRunResult) -> tuple[Mapping[str, Any], ...]:
    raw = result.backend_metrics.get("matches")
    if raw is None:
        return ()
    if not isinstance(raw, list):
        raise ValueError("recovery matches metric must be a list")
    matches: list[Mapping[str, Any]] = []
    for item in raw:
        if not isinstance(item, Mapping):
            raise ValueError("each recovery match metric must be a mapping")
        matches.append(item)
    return tuple(matches)


def _non_negative_int_metric(result: FollowerRunResult, name: str) -> int:
    raw = result.backend_metrics.get(name, 0)
    if isinstance(raw, bool) or not isinstance(raw, int) or raw < 0:
        raise ValueError(f"{name} metric must be a non-negative integer")
    return raw


def _required_int(record: Mapping[str, Any], name: str) -> int:
    raw = record.get(name)
    if isinstance(raw, bool) or not isinstance(raw, int) or raw < 0:
        raise ValueError(f"recovery match {name} must be a non-negative integer")
    return raw


def _required_text(record: Mapping[str, Any], name: str) -> str:
    raw = record.get(name)
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError(f"recovery match {name} must be non-empty text")
    return raw


def _default_abstentions(*, has_unmatched: bool) -> tuple[EvidenceAbstentionV1, ...]:
    items = [
        EvidenceAbstentionV1(
            kind=AbstentionKind.PITCH_ERROR_IDENTITY,
            reason=(
                "Current alignment/recovery evidence does not establish note correctness "
                "for every performed event."
            ),
        ),
        EvidenceAbstentionV1(
            kind=AbstentionKind.ARTICULATION,
            reason="No articulation evidence is present in the current contracts.",
        ),
        EvidenceAbstentionV1(
            kind=AbstentionKind.DYNAMICS,
            reason="No calibrated dynamics evidence is present in the current contracts.",
        ),
        EvidenceAbstentionV1(
            kind=AbstentionKind.MUSICAL_INTENT,
            reason="Measured timing or recovery facts do not establish musical intent.",
        ),
        EvidenceAbstentionV1(
            kind=AbstentionKind.PEDAGOGICAL_GRADE,
            reason=(
                "Research evidence is not converted into a student grade, score, "
                "or pedagogical authority."
            ),
        ),
    ]
    if has_unmatched:
        items.append(
            EvidenceAbstentionV1(
                kind=AbstentionKind.UNMATCHED_OBSERVATION_SEMANTICS,
                reason=(
                    "An unmatched observation cannot be distinguished as wrong note, "
                    "extra note, ornament, or upstream transcription error from recovery "
                    "evidence alone."
                ),
                source_reference="recovery:unmatched_observations",
            )
        )
    return tuple(items)


def _summary(
    events: tuple[PerformanceEvidenceEventV1, ...],
    abstentions: tuple[EvidenceAbstentionV1, ...],
) -> PerformanceErrorIntelligenceSummaryV1:
    counts: dict[str, int] = {}
    for event in events:
        counts[event.kind.value] = counts.get(event.kind.value, 0) + 1

    timing = [
        abs(event.deviation_ms)
        for event in events
        if event.kind in {EvidenceKind.TIMING_EARLY, EvidenceKind.TIMING_LATE}
        and event.deviation_ms is not None
    ]
    return PerformanceErrorIntelligenceSummaryV1(
        evidence_event_count=len(events),
        counts_by_kind=counts,
        events_with_confidence=sum(event.confidence is not None for event in events),
        events_without_confidence=sum(event.confidence is None for event in events),
        abstention_count=len(abstentions),
        timing_event_count=len(timing),
        mean_absolute_timing_deviation_ms=mean(timing) if timing else None,
        max_absolute_timing_deviation_ms=max(timing) if timing else None,
        unmatched_observation_count=sum(
            event.count or 1
            for event in events
            if event.kind is EvidenceKind.UNMATCHED_OBSERVATION
        ),
        skipped_score_event_count=sum(
            event.count or 1
            for event in events
            if event.kind is EvidenceKind.SKIPPED_SCORE_REGION
        ),
        score_discontinuity_events=sum(
            event.kind is EvidenceKind.SCORE_DISCONTINUITY for event in events
        ),
        performance_gap_events=sum(
            event.kind is EvidenceKind.PERFORMANCE_GAP for event in events
        ),
    )


def build_performance_error_intelligence_report(
    alignment_report: PerformanceAlignmentReportV1,
    *,
    recovery_result: FollowerRunResult | None = None,
) -> PerformanceErrorIntelligenceReportV1:
    events: list[PerformanceEvidenceEventV1] = []
    counter = 0

    def add_event(**kwargs: Any) -> None:
        nonlocal counter
        counter += 1
        events.append(
            PerformanceEvidenceEventV1(
                evidence_id=f"sf08-evidence-{counter:04d}",
                **kwargs,
            )
        )

    for point in alignment_report.points:
        if point.timing_class in {TimingClass.EARLY, TimingClass.LATE}:
            add_event(
                kind=(
                    EvidenceKind.TIMING_EARLY
                    if point.timing_class is TimingClass.EARLY
                    else EvidenceKind.TIMING_LATE
                ),
                origin=EvidenceOrigin.PERFORMANCE_ALIGNMENT,
                source_reference=f"alignment:sequence:{point.sequence_id}",
                sequence_id=point.sequence_id,
                segment_id=point.segment_id,
                score_beat=point.score_beat,
                performance_time_s=point.performance_time_s,
                deviation_ms=point.segment_deviation_s * 1000.0,
                confidence=point.confidence,
            )

        if point.boundary_reason is SegmentBoundaryReason.SCORE_DISCONTINUITY:
            add_event(
                kind=EvidenceKind.SCORE_DISCONTINUITY,
                origin=EvidenceOrigin.PERFORMANCE_ALIGNMENT,
                source_reference=f"alignment:sequence:{point.sequence_id}",
                sequence_id=point.sequence_id,
                segment_id=point.segment_id,
                score_beat=point.score_beat,
                performance_time_s=point.performance_time_s,
                confidence=point.confidence,
            )
        elif point.boundary_reason is SegmentBoundaryReason.PERFORMANCE_GAP:
            add_event(
                kind=EvidenceKind.PERFORMANCE_GAP,
                origin=EvidenceOrigin.PERFORMANCE_ALIGNMENT,
                source_reference=f"alignment:sequence:{point.sequence_id}",
                sequence_id=point.sequence_id,
                segment_id=point.segment_id,
                score_beat=point.score_beat,
                performance_time_s=point.performance_time_s,
                confidence=point.confidence,
            )

    unmatched_count = 0
    recovery_backend = None
    if recovery_result is not None:
        recovery_backend = recovery_result.backend
        unmatched_count = _non_negative_int_metric(
            recovery_result,
            "unmatched_observations",
        )
        if unmatched_count:
            add_event(
                kind=EvidenceKind.UNMATCHED_OBSERVATION,
                origin=EvidenceOrigin.RECOVERY_AUDIT,
                source_reference=(
                    f"recovery:{recovery_result.backend}:unmatched_observations"
                ),
                count=unmatched_count,
            )

        previous_score_index: int | None = None
        for record in _recovery_matches(recovery_result):
            score_index = _required_int(record, "score_index")
            transition = _required_text(record, "transition")
            event_id = _required_text(record, "event_id")
            if transition == "forward_skip":
                if previous_score_index is None or score_index <= previous_score_index + 1:
                    raise ValueError("forward_skip recovery match has inconsistent score indices")
                skipped = score_index - previous_score_index - 1
                add_event(
                    kind=EvidenceKind.SKIPPED_SCORE_REGION,
                    origin=EvidenceOrigin.RECOVERY_AUDIT,
                    source_reference=f"recovery:event:{event_id}",
                    score_index_start=previous_score_index + 1,
                    score_index_end=score_index - 1,
                    count=skipped,
                )
            previous_score_index = score_index

    abstentions = _default_abstentions(has_unmatched=unmatched_count > 0)
    event_tuple = tuple(events)
    return PerformanceErrorIntelligenceReportV1(
        source_alignment_schema=alignment_report.schema_version,
        source_recovery_backend=recovery_backend,
        events=event_tuple,
        abstentions=abstentions,
        summary=_summary(event_tuple, abstentions),
    )
