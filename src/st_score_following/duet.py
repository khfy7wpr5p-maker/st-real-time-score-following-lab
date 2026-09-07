from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from math import isfinite
from statistics import mean, median
from typing import Any

from .contracts import ConfidenceV1, PerformanceEventV1
from .followers.base import AlignmentPoint, FollowerRunResult
from .recovery import RecoveryAwareSymbolicFollower, RecoveryMatch
from .symbolic import SymbolicScoreEvent


class SharedPositionStatus(StrEnum):
    CONSENSUS = "consensus"
    SINGLE_PART = "single_part"
    DIVERGENT = "divergent"


@dataclass(frozen=True, slots=True)
class DuetPartInputV1:
    part_id: str
    performer_id: str
    score_events: tuple[SymbolicScoreEvent, ...]
    observations: tuple[PerformanceEventV1, ...]
    schema_version: str = field(default="duet_part_input_v1", init=False)

    def __post_init__(self) -> None:
        if not self.part_id.strip():
            raise ValueError("part_id must be non-empty")
        if not self.performer_id.strip():
            raise ValueError("performer_id must be non-empty")
        if not self.score_events:
            raise ValueError("score_events must not be empty")
        event_ids = [event.event_id for event in self.observations]
        if len(event_ids) != len(set(event_ids)):
            raise ValueError("observation event_id values must be unique within a part")
        for previous, current in zip(
            self.observations,
            self.observations[1:],
            strict=False,
        ):
            if current.observed_at_s < previous.observed_at_s:
                raise ValueError("observations must be ordered by observed_at_s")


@dataclass(frozen=True, slots=True)
class DuetPartAlignmentV1:
    part_id: str
    performer_id: str
    backend: str
    alignment_path: tuple[AlignmentPoint, ...]
    matches: tuple[RecoveryMatch, ...]
    matched_events: int
    unmatched_observations: int
    forward_skipped_score_events: int
    backward_jumps: int
    pause_gaps: int
    unavailable_confidence: int
    schema_version: str = field(default="duet_part_alignment_v1", init=False)

    @property
    def final_score_beat(self) -> float | None:
        if not self.alignment_path:
            return None
        return self.alignment_path[-1].score_beat

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "part_id": self.part_id,
            "performer_id": self.performer_id,
            "backend": self.backend,
            "matched_events": self.matched_events,
            "unmatched_observations": self.unmatched_observations,
            "forward_skipped_score_events": self.forward_skipped_score_events,
            "backward_jumps": self.backward_jumps,
            "pause_gaps": self.pause_gaps,
            "unavailable_confidence": self.unavailable_confidence,
            "final_score_beat": self.final_score_beat,
            "alignment_path": [asdict(point) for point in self.alignment_path],
            "matches": [match.to_dict() for match in self.matches],
        }


@dataclass(frozen=True, slots=True)
class DuetPartPositionV1:
    part_id: str
    score_beat: float
    last_update_s: float
    age_s: float
    schema_version: str = field(default="duet_part_position_v1", init=False)

    def __post_init__(self) -> None:
        if not self.part_id.strip():
            raise ValueError("part_id must be non-empty")
        for name, value in (
            ("score_beat", self.score_beat),
            ("last_update_s", self.last_update_s),
            ("age_s", self.age_s),
        ):
            if not isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and >= 0")


@dataclass(frozen=True, slots=True)
class DuetSharedPositionSnapshotV1:
    sequence_id: int
    observed_at_s: float
    shared_score_beat: float
    status: SharedPositionStatus
    positions: tuple[DuetPartPositionV1, ...]
    contributing_part_ids: tuple[str, ...]
    stale_part_ids: tuple[str, ...]
    unavailable_part_ids: tuple[str, ...]
    spread_beats: float
    confidence: ConfidenceV1 | None = None
    method: str = field(default="median_recent_part_positions", init=False)
    schema_version: str = field(default="duet_shared_position_snapshot_v1", init=False)

    def __post_init__(self) -> None:
        if self.sequence_id < 0:
            raise ValueError("sequence_id must be >= 0")
        if not isfinite(self.observed_at_s) or self.observed_at_s < 0:
            raise ValueError("observed_at_s must be finite and >= 0")
        if not isfinite(self.shared_score_beat) or self.shared_score_beat < 0:
            raise ValueError("shared_score_beat must be finite and >= 0")
        if not isfinite(self.spread_beats) or self.spread_beats < 0:
            raise ValueError("spread_beats must be finite and >= 0")
        if not self.positions or not self.contributing_part_ids:
            raise ValueError("shared snapshot must have at least one contributing part")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass(frozen=True, slots=True)
class DuetAsynchronyPointV1:
    score_beat: float
    occurrence_index: int
    first_part_id: str
    second_part_id: str
    first_time_s: float
    second_time_s: float
    signed_delta_ms: float
    absolute_delta_ms: float
    schema_version: str = field(default="duet_asynchrony_point_v1", init=False)

    def __post_init__(self) -> None:
        if not isfinite(self.score_beat) or self.score_beat < 0:
            raise ValueError("score_beat must be finite and >= 0")
        if self.occurrence_index < 0:
            raise ValueError("occurrence_index must be >= 0")
        if not self.first_part_id.strip() or not self.second_part_id.strip():
            raise ValueError("part IDs must be non-empty")
        for name, value in (
            ("first_time_s", self.first_time_s),
            ("second_time_s", self.second_time_s),
            ("signed_delta_ms", self.signed_delta_ms),
            ("absolute_delta_ms", self.absolute_delta_ms),
        ):
            if not isfinite(value):
                raise ValueError(f"{name} must be finite")
        if self.first_time_s < 0 or self.second_time_s < 0 or self.absolute_delta_ms < 0:
            raise ValueError("times and absolute_delta_ms must be >= 0")


@dataclass(frozen=True, slots=True)
class DuetAnalysisSummaryV1:
    part_count: int
    snapshot_count: int
    consensus_snapshots: int
    single_part_snapshots: int
    divergent_snapshots: int
    common_asynchrony_points: int
    mean_absolute_asynchrony_ms: float | None
    median_absolute_asynchrony_ms: float | None
    p95_absolute_asynchrony_ms: float | None
    max_absolute_asynchrony_ms: float | None
    max_position_spread_beats: float
    shared_confidence_available: bool
    schema_version: str = field(default="duet_analysis_summary_v1", init=False)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DuetAnalysisReportV1:
    parts: tuple[DuetPartAlignmentV1, ...]
    shared_positions: tuple[DuetSharedPositionSnapshotV1, ...]
    asynchrony: tuple[DuetAsynchronyPointV1, ...]
    summary: DuetAnalysisSummaryV1
    stale_after_s: float
    divergence_threshold_beats: float
    authority_boundary: str = field(default="duet_research_not_ensemble_authority", init=False)
    schema_version: str = field(default="duet_analysis_report_v1", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "authority_boundary": self.authority_boundary,
            "stale_after_s": self.stale_after_s,
            "divergence_threshold_beats": self.divergence_threshold_beats,
            "summary": self.summary.to_dict(),
            "parts": [part.to_dict() for part in self.parts],
            "shared_positions": [snapshot.to_dict() for snapshot in self.shared_positions],
            "asynchrony": [asdict(point) for point in self.asynchrony],
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True, allow_nan=False)


def _integer_metric(result: FollowerRunResult, name: str) -> int:
    raw = result.backend_metrics.get(name, 0)
    if isinstance(raw, bool) or not isinstance(raw, int) or raw < 0:
        raise ValueError(f"{name} metric must be a non-negative integer")
    return raw


def _matches(result: FollowerRunResult) -> tuple[RecoveryMatch, ...]:
    raw = result.backend_metrics.get("matches", [])
    if not isinstance(raw, list):
        raise ValueError("matches metric must be a list")
    items: list[RecoveryMatch] = []
    for record in raw:
        if not isinstance(record, Mapping):
            raise ValueError("each match metric must be a mapping")
        items.append(RecoveryMatch(**dict(record)))
    return tuple(items)


def _p95(values: list[float]) -> float:
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(0.95 * len(ordered) + 0.999999) - 1))
    return ordered[index]


class DuetAnalyzer:
    """Research-only two-part analyzer built from independent single-part followers."""

    def __init__(
        self,
        parts: Iterable[DuetPartInputV1],
        *,
        stale_after_s: float = 0.75,
        divergence_threshold_beats: float = 1.5,
        recovery_pause_gap_s: float = 1.5,
    ) -> None:
        self._parts = tuple(parts)
        if len(self._parts) != 2:
            raise ValueError("DuetAnalyzer requires exactly two parts")
        part_ids = [part.part_id for part in self._parts]
        performer_ids = [part.performer_id for part in self._parts]
        if len(set(part_ids)) != 2:
            raise ValueError("duet part_id values must be unique")
        if len(set(performer_ids)) != 2:
            raise ValueError("duet performer_id values must be unique")
        if not isfinite(stale_after_s) or stale_after_s <= 0:
            raise ValueError("stale_after_s must be finite and > 0")
        if not isfinite(divergence_threshold_beats) or divergence_threshold_beats < 0:
            raise ValueError("divergence_threshold_beats must be finite and >= 0")
        if not isfinite(recovery_pause_gap_s) or recovery_pause_gap_s <= 0:
            raise ValueError("recovery_pause_gap_s must be finite and > 0")
        self._stale_after_s = stale_after_s
        self._divergence_threshold_beats = divergence_threshold_beats
        self._recovery_pause_gap_s = recovery_pause_gap_s

    def _run_part(self, part: DuetPartInputV1) -> DuetPartAlignmentV1:
        result = RecoveryAwareSymbolicFollower(
            part.score_events,
            pause_gap_s=self._recovery_pause_gap_s,
        ).run_events(part.observations)
        return DuetPartAlignmentV1(
            part_id=part.part_id,
            performer_id=part.performer_id,
            backend=result.backend,
            alignment_path=result.alignment_path,
            matches=_matches(result),
            matched_events=_integer_metric(result, "matched_events"),
            unmatched_observations=_integer_metric(result, "unmatched_observations"),
            forward_skipped_score_events=_integer_metric(
                result,
                "forward_skipped_score_events",
            ),
            backward_jumps=_integer_metric(result, "backward_jumps"),
            pause_gaps=_integer_metric(result, "pause_gaps"),
            unavailable_confidence=_integer_metric(result, "unavailable_confidence"),
        )

    def _shared_snapshots(
        self,
        parts: tuple[DuetPartAlignmentV1, ...],
    ) -> tuple[DuetSharedPositionSnapshotV1, ...]:
        all_part_ids = tuple(part.part_id for part in parts)
        timeline = sorted(
            (
                (match.observed_at_s, part.part_id, match.score_beat)
                for part in parts
                for match in part.matches
            ),
            key=lambda item: (item[0], item[1]),
        )
        latest: dict[str, tuple[float, float]] = {}
        snapshots: list[DuetSharedPositionSnapshotV1] = []
        for sequence_id, (observed_at_s, part_id, score_beat) in enumerate(timeline):
            latest[part_id] = (score_beat, observed_at_s)
            positions: list[DuetPartPositionV1] = []
            stale: list[str] = []
            unavailable: list[str] = []
            for candidate_id in all_part_ids:
                latest_value = latest.get(candidate_id)
                if latest_value is None:
                    unavailable.append(candidate_id)
                    continue
                candidate_beat, candidate_time = latest_value
                age_s = observed_at_s - candidate_time
                if age_s > self._stale_after_s:
                    stale.append(candidate_id)
                    continue
                positions.append(
                    DuetPartPositionV1(
                        part_id=candidate_id,
                        score_beat=candidate_beat,
                        last_update_s=candidate_time,
                        age_s=age_s,
                    )
                )
            beats = [position.score_beat for position in positions]
            shared_score_beat = float(median(beats))
            spread_beats = max(beats) - min(beats)
            if len(positions) == 1:
                status = SharedPositionStatus.SINGLE_PART
            elif spread_beats > self._divergence_threshold_beats:
                status = SharedPositionStatus.DIVERGENT
            else:
                status = SharedPositionStatus.CONSENSUS
            snapshots.append(
                DuetSharedPositionSnapshotV1(
                    sequence_id=sequence_id,
                    observed_at_s=observed_at_s,
                    shared_score_beat=shared_score_beat,
                    status=status,
                    positions=tuple(positions),
                    contributing_part_ids=tuple(
                        position.part_id for position in positions
                    ),
                    stale_part_ids=tuple(stale),
                    unavailable_part_ids=tuple(unavailable),
                    spread_beats=spread_beats,
                )
            )
        return tuple(snapshots)

    @staticmethod
    def _asynchrony(
        parts: tuple[DuetPartAlignmentV1, ...],
    ) -> tuple[DuetAsynchronyPointV1, ...]:
        first, second = parts
        first_by_beat: dict[float, list[float]] = {}
        second_by_beat: dict[float, list[float]] = {}
        for match in first.matches:
            first_by_beat.setdefault(match.score_beat, []).append(match.observed_at_s)
        for match in second.matches:
            second_by_beat.setdefault(match.score_beat, []).append(match.observed_at_s)

        points: list[DuetAsynchronyPointV1] = []
        for score_beat in sorted(set(first_by_beat) & set(second_by_beat)):
            first_times = sorted(first_by_beat[score_beat])
            second_times = sorted(second_by_beat[score_beat])
            for occurrence_index, (first_time, second_time) in enumerate(
                zip(first_times, second_times, strict=False)
            ):
                signed_delta_ms = (second_time - first_time) * 1000.0
                points.append(
                    DuetAsynchronyPointV1(
                        score_beat=score_beat,
                        occurrence_index=occurrence_index,
                        first_part_id=first.part_id,
                        second_part_id=second.part_id,
                        first_time_s=first_time,
                        second_time_s=second_time,
                        signed_delta_ms=signed_delta_ms,
                        absolute_delta_ms=abs(signed_delta_ms),
                    )
                )
        return tuple(points)

    def run(self) -> DuetAnalysisReportV1:
        parts = tuple(self._run_part(part) for part in self._parts)
        snapshots = self._shared_snapshots(parts)
        asynchrony = self._asynchrony(parts)
        absolute_async = [point.absolute_delta_ms for point in asynchrony]
        summary = DuetAnalysisSummaryV1(
            part_count=2,
            snapshot_count=len(snapshots),
            consensus_snapshots=sum(
                snapshot.status is SharedPositionStatus.CONSENSUS
                for snapshot in snapshots
            ),
            single_part_snapshots=sum(
                snapshot.status is SharedPositionStatus.SINGLE_PART
                for snapshot in snapshots
            ),
            divergent_snapshots=sum(
                snapshot.status is SharedPositionStatus.DIVERGENT
                for snapshot in snapshots
            ),
            common_asynchrony_points=len(asynchrony),
            mean_absolute_asynchrony_ms=(
                mean(absolute_async) if absolute_async else None
            ),
            median_absolute_asynchrony_ms=(
                median(absolute_async) if absolute_async else None
            ),
            p95_absolute_asynchrony_ms=(
                _p95(absolute_async) if absolute_async else None
            ),
            max_absolute_asynchrony_ms=(
                max(absolute_async) if absolute_async else None
            ),
            max_position_spread_beats=max(
                (snapshot.spread_beats for snapshot in snapshots),
                default=0.0,
            ),
            shared_confidence_available=False,
        )
        return DuetAnalysisReportV1(
            parts=parts,
            shared_positions=snapshots,
            asynchrony=asynchrony,
            summary=summary,
            stale_after_s=self._stale_after_s,
            divergence_threshold_beats=self._divergence_threshold_beats,
        )
