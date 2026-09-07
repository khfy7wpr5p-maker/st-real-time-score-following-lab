from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from io import StringIO
from math import isfinite
from statistics import mean, median

from .contracts import ConfidenceV1
from .followers.base import AlignmentPoint


class TimingClass(StrEnum):
    EARLY = "early"
    ON_TIME = "on_time"
    LATE = "late"


class SegmentBoundaryReason(StrEnum):
    INITIAL = "initial"
    SCORE_DISCONTINUITY = "score_discontinuity"
    PERFORMANCE_GAP = "performance_gap"


@dataclass(frozen=True, slots=True)
class AlignmentProvenanceV1:
    backend: str
    backend_version: str | None = None
    method: str | None = None
    input_type: str | None = None
    run_id: str | None = None
    schema_version: str = field(default="alignment_provenance_v1", init=False)

    def __post_init__(self) -> None:
        if not self.backend.strip():
            raise ValueError("backend must be non-empty")

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PerformanceAlignmentPointV1:
    sequence_id: int
    segment_id: int
    boundary_reason: SegmentBoundaryReason | None
    score_beat: float
    score_time_s: float
    performance_time_s: float
    absolute_deviation_s: float
    segment_deviation_s: float
    timing_class: TimingClass
    local_tempo_bpm: float | None
    confidence: ConfidenceV1 | None
    schema_version: str = field(default="performance_alignment_point_v1", init=False)

    def __post_init__(self) -> None:
        if self.sequence_id < 0 or self.segment_id < 0:
            raise ValueError("sequence_id and segment_id must be >= 0")
        for name, value in (
            ("score_beat", self.score_beat),
            ("score_time_s", self.score_time_s),
            ("performance_time_s", self.performance_time_s),
            ("absolute_deviation_s", self.absolute_deviation_s),
            ("segment_deviation_s", self.segment_deviation_s),
        ):
            if not isfinite(value):
                raise ValueError(f"{name} must be finite")
        if self.score_beat < 0 or self.score_time_s < 0 or self.performance_time_s < 0:
            raise ValueError("score/performance coordinates must be >= 0")
        if self.local_tempo_bpm is not None:
            if not isfinite(self.local_tempo_bpm) or self.local_tempo_bpm <= 0:
                raise ValueError("local_tempo_bpm must be finite and > 0 when present")

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["timing_class"] = self.timing_class.value
        data["boundary_reason"] = (
            None if self.boundary_reason is None else self.boundary_reason.value
        )
        return data


@dataclass(frozen=True, slots=True)
class PerformanceAlignmentSummaryV1:
    point_count: int
    segment_count: int
    mean_absolute_segment_deviation_ms: float
    median_absolute_segment_deviation_ms: float
    p95_absolute_segment_deviation_ms: float
    early_count: int
    on_time_count: int
    late_count: int
    local_tempo_samples: int
    mean_local_tempo_bpm: float | None
    median_local_tempo_bpm: float | None
    min_local_tempo_bpm: float | None
    max_local_tempo_bpm: float | None
    score_discontinuities: int
    performance_gap_boundaries: int
    schema_version: str = field(default="performance_alignment_summary_v1", init=False)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PerformanceAlignmentReportV1:
    provenance: AlignmentProvenanceV1
    reference_bpm: float
    on_time_tolerance_ms: float
    pause_gap_s: float
    points: tuple[PerformanceAlignmentPointV1, ...]
    summary: PerformanceAlignmentSummaryV1
    schema_version: str = field(default="performance_alignment_report_v1", init=False)

    def __post_init__(self) -> None:
        if not isfinite(self.reference_bpm) or self.reference_bpm <= 0:
            raise ValueError("reference_bpm must be finite and > 0")
        if not isfinite(self.on_time_tolerance_ms) or self.on_time_tolerance_ms < 0:
            raise ValueError("on_time_tolerance_ms must be finite and >= 0")
        if not isfinite(self.pause_gap_s) or self.pause_gap_s <= 0:
            raise ValueError("pause_gap_s must be finite and > 0")
        if not self.points:
            raise ValueError("points must not be empty")

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "provenance": self.provenance.to_dict(),
            "reference_bpm": self.reference_bpm,
            "on_time_tolerance_ms": self.on_time_tolerance_ms,
            "pause_gap_s": self.pause_gap_s,
            "summary": self.summary.to_dict(),
            "points": [point.to_dict() for point in self.points],
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True, allow_nan=False)

    def to_csv(self) -> str:
        fieldnames = [
            "sequence_id",
            "segment_id",
            "boundary_reason",
            "score_beat",
            "score_time_s",
            "performance_time_s",
            "absolute_deviation_s",
            "segment_deviation_s",
            "timing_class",
            "local_tempo_bpm",
            "confidence_value",
            "confidence_source",
            "confidence_calibrated",
            "confidence_reason",
        ]
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for point in self.points:
            confidence = point.confidence
            writer.writerow(
                {
                    "sequence_id": point.sequence_id,
                    "segment_id": point.segment_id,
                    "boundary_reason": (
                        "" if point.boundary_reason is None else point.boundary_reason.value
                    ),
                    "score_beat": point.score_beat,
                    "score_time_s": point.score_time_s,
                    "performance_time_s": point.performance_time_s,
                    "absolute_deviation_s": point.absolute_deviation_s,
                    "segment_deviation_s": point.segment_deviation_s,
                    "timing_class": point.timing_class.value,
                    "local_tempo_bpm": (
                        "" if point.local_tempo_bpm is None else point.local_tempo_bpm
                    ),
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


def _p95(values: list[float]) -> float:
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(0.95 * len(ordered) + 0.999999) - 1))
    return ordered[index]


def _classify(deviation_s: float, tolerance_s: float) -> TimingClass:
    if deviation_s < -tolerance_s:
        return TimingClass.EARLY
    if deviation_s > tolerance_s:
        return TimingClass.LATE
    return TimingClass.ON_TIME


def build_performance_alignment_report(
    path: tuple[AlignmentPoint, ...],
    *,
    reference_bpm: float,
    provenance: AlignmentProvenanceV1,
    on_time_tolerance_ms: float = 50.0,
    pause_gap_s: float = 1.5,
    confidences: tuple[ConfidenceV1 | None, ...] | None = None,
) -> PerformanceAlignmentReportV1:
    if not path:
        raise ValueError("path must not be empty")
    if not isfinite(reference_bpm) or reference_bpm <= 0:
        raise ValueError("reference_bpm must be finite and > 0")
    if not isfinite(on_time_tolerance_ms) or on_time_tolerance_ms < 0:
        raise ValueError("on_time_tolerance_ms must be finite and >= 0")
    if not isfinite(pause_gap_s) or pause_gap_s <= 0:
        raise ValueError("pause_gap_s must be finite and > 0")
    if confidences is not None and len(confidences) != len(path):
        raise ValueError("confidences length must match path length")

    tolerance_s = on_time_tolerance_ms / 1000.0
    seconds_per_beat = 60.0 / reference_bpm
    points: list[PerformanceAlignmentPointV1] = []
    segment_id = 0
    segment_score_origin = 0.0
    segment_performance_origin = 0.0
    previous: AlignmentPoint | None = None

    for sequence_id, source in enumerate(path):
        if not isfinite(source.score_beat) or source.score_beat < 0:
            raise ValueError("score beats must be finite and >= 0")
        if not isfinite(source.performance_time_s) or source.performance_time_s < 0:
            raise ValueError("performance times must be finite and >= 0")
        if previous is not None and source.performance_time_s < previous.performance_time_s:
            raise ValueError("performance times must be non-decreasing")

        score_time_s = source.score_beat * seconds_per_beat
        boundary_reason: SegmentBoundaryReason | None = None
        local_tempo_bpm: float | None = None

        if previous is None:
            boundary_reason = SegmentBoundaryReason.INITIAL
            segment_score_origin = score_time_s
            segment_performance_origin = source.performance_time_s
        else:
            score_delta = source.score_beat - previous.score_beat
            performance_delta = source.performance_time_s - previous.performance_time_s
            if score_delta <= 0:
                segment_id += 1
                boundary_reason = SegmentBoundaryReason.SCORE_DISCONTINUITY
                segment_score_origin = score_time_s
                segment_performance_origin = source.performance_time_s
            elif performance_delta >= pause_gap_s:
                segment_id += 1
                boundary_reason = SegmentBoundaryReason.PERFORMANCE_GAP
                segment_score_origin = score_time_s
                segment_performance_origin = source.performance_time_s
            elif performance_delta > 0:
                local_tempo_bpm = 60.0 * score_delta / performance_delta

        absolute_deviation_s = source.performance_time_s - score_time_s
        segment_deviation_s = (
            source.performance_time_s - segment_performance_origin
        ) - (score_time_s - segment_score_origin)
        confidence = None if confidences is None else confidences[sequence_id]
        points.append(
            PerformanceAlignmentPointV1(
                sequence_id=sequence_id,
                segment_id=segment_id,
                boundary_reason=boundary_reason,
                score_beat=source.score_beat,
                score_time_s=score_time_s,
                performance_time_s=source.performance_time_s,
                absolute_deviation_s=absolute_deviation_s,
                segment_deviation_s=segment_deviation_s,
                timing_class=_classify(segment_deviation_s, tolerance_s),
                local_tempo_bpm=local_tempo_bpm,
                confidence=confidence,
            )
        )
        previous = source

    absolute_ms = [abs(point.segment_deviation_s) * 1000.0 for point in points]
    tempos = [point.local_tempo_bpm for point in points if point.local_tempo_bpm is not None]
    summary = PerformanceAlignmentSummaryV1(
        point_count=len(points),
        segment_count=points[-1].segment_id + 1,
        mean_absolute_segment_deviation_ms=mean(absolute_ms),
        median_absolute_segment_deviation_ms=median(absolute_ms),
        p95_absolute_segment_deviation_ms=_p95(absolute_ms),
        early_count=sum(point.timing_class is TimingClass.EARLY for point in points),
        on_time_count=sum(point.timing_class is TimingClass.ON_TIME for point in points),
        late_count=sum(point.timing_class is TimingClass.LATE for point in points),
        local_tempo_samples=len(tempos),
        mean_local_tempo_bpm=mean(tempos) if tempos else None,
        median_local_tempo_bpm=median(tempos) if tempos else None,
        min_local_tempo_bpm=min(tempos) if tempos else None,
        max_local_tempo_bpm=max(tempos) if tempos else None,
        score_discontinuities=sum(
            point.boundary_reason is SegmentBoundaryReason.SCORE_DISCONTINUITY
            for point in points
        ),
        performance_gap_boundaries=sum(
            point.boundary_reason is SegmentBoundaryReason.PERFORMANCE_GAP for point in points
        ),
    )
    return PerformanceAlignmentReportV1(
        provenance=provenance,
        reference_bpm=reference_bpm,
        on_time_tolerance_ms=on_time_tolerance_ms,
        pause_gap_s=pause_gap_s,
        points=tuple(points),
        summary=summary,
    )
