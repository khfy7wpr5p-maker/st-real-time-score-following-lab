from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from itertools import combinations
from math import isfinite
from statistics import mean, median
from typing import Any

from .contracts import ConfidenceV1, PerformanceEventV1
from .followers.base import AlignmentPoint, FollowerRunResult
from .recovery import RecoveryAwareSymbolicFollower, RecoveryMatch
from .symbolic import SymbolicScoreEvent


class QuartetPositionStatus(StrEnum):
    FULL_CONSENSUS = "full_consensus"
    QUORUM_CONSENSUS = "quorum_consensus"
    DIVERGENT = "divergent"
    INSUFFICIENT_QUORUM = "insufficient_quorum"


@dataclass(frozen=True, slots=True)
class QuartetPartInputV1:
    part_id: str
    performer_id: str
    channel_id: str
    score_events: tuple[SymbolicScoreEvent, ...]
    observations: tuple[PerformanceEventV1, ...]
    schema_version: str = field(default="quartet_part_input_v1", init=False)

    def __post_init__(self) -> None:
        for name, value in (
            ("part_id", self.part_id),
            ("performer_id", self.performer_id),
            ("channel_id", self.channel_id),
        ):
            if not value.strip():
                raise ValueError(f"{name} must be non-empty")
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
class QuartetPartAlignmentV1:
    part_id: str
    performer_id: str
    channel_id: str
    backend: str
    alignment_path: tuple[AlignmentPoint, ...]
    matches: tuple[RecoveryMatch, ...]
    matched_events: int
    unmatched_observations: int
    forward_skipped_score_events: int
    backward_jumps: int
    pause_gaps: int
    unavailable_confidence: int
    schema_version: str = field(default="quartet_part_alignment_v1", init=False)

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
            "channel_id": self.channel_id,
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
class QuartetPartPositionV1:
    part_id: str
    channel_id: str
    score_beat: float
    last_update_s: float
    age_s: float
    schema_version: str = field(default="quartet_part_position_v1", init=False)

    def __post_init__(self) -> None:
        if not self.part_id.strip() or not self.channel_id.strip():
            raise ValueError("part_id and channel_id must be non-empty")
        for name, value in (
            ("score_beat", self.score_beat),
            ("last_update_s", self.last_update_s),
            ("age_s", self.age_s),
        ):
            if not isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and >= 0")


@dataclass(frozen=True, slots=True)
class QuartetSharedPositionSnapshotV1:
    sequence_id: int
    observed_at_s: float
    shared_score_beat: float | None
    status: QuartetPositionStatus
    positions: tuple[QuartetPartPositionV1, ...]
    contributing_part_ids: tuple[str, ...]
    stale_part_ids: tuple[str, ...]
    unavailable_part_ids: tuple[str, ...]
    coverage_ratio: float
    spread_beats: float | None
    required_quorum_parts: int
    confidence: ConfidenceV1 | None = None
    method: str = field(default="median_recent_part_positions_with_quorum", init=False)
    schema_version: str = field(default="quartet_shared_position_snapshot_v1", init=False)

    def __post_init__(self) -> None:
        if self.sequence_id < 0:
            raise ValueError("sequence_id must be >= 0")
        if not isfinite(self.observed_at_s) or self.observed_at_s < 0:
            raise ValueError("observed_at_s must be finite and >= 0")
        if not isfinite(self.coverage_ratio) or not 0 <= self.coverage_ratio <= 1:
            raise ValueError("coverage_ratio must be within [0, 1]")
        if self.required_quorum_parts < 1:
            raise ValueError("required_quorum_parts must be >= 1")
        if not self.positions or not self.contributing_part_ids:
            raise ValueError("snapshot must contain at least one recent part position")
        if len(self.positions) != len(self.contributing_part_ids):
            raise ValueError("positions and contributing_part_ids must have equal length")
        if len(self.positions) < self.required_quorum_parts:
            if self.status is not QuartetPositionStatus.INSUFFICIENT_QUORUM:
                raise ValueError("below-quorum snapshot must be insufficient_quorum")
            if self.shared_score_beat is not None or self.spread_beats is not None:
                raise ValueError("below-quorum snapshot must not publish shared position")
        else:
            if self.status is QuartetPositionStatus.INSUFFICIENT_QUORUM:
                raise ValueError("quorum snapshot cannot be insufficient_quorum")
            if self.shared_score_beat is None or self.spread_beats is None:
                raise ValueError("quorum snapshot must publish shared position and spread")
            if not isfinite(self.shared_score_beat) or self.shared_score_beat < 0:
                raise ValueError("shared_score_beat must be finite and >= 0")
            if not isfinite(self.spread_beats) or self.spread_beats < 0:
                raise ValueError("spread_beats must be finite and >= 0")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass(frozen=True, slots=True)
class QuartetPairwiseAsynchronyPointV1:
    score_beat: float
    occurrence_index: int
    first_part_id: str
    second_part_id: str
    first_time_s: float
    second_time_s: float
    signed_delta_ms: float
    absolute_delta_ms: float
    schema_version: str = field(default="quartet_pairwise_asynchrony_point_v1", init=False)

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
class QuartetAnalysisSummaryV1:
    part_count: int
    channel_count: int
    pair_count: int
    snapshot_count: int
    full_consensus_snapshots: int
    quorum_consensus_snapshots: int
    divergent_snapshots: int
    insufficient_quorum_snapshots: int
    degraded_insufficient_quorum_snapshots: int
    pairwise_asynchrony_points: int
    mean_absolute_asynchrony_ms: float | None
    median_absolute_asynchrony_ms: float | None
    p95_absolute_asynchrony_ms: float | None
    max_absolute_asynchrony_ms: float | None
    max_position_spread_beats: float
    max_stale_parts: int
    shared_confidence_available: bool
    schema_version: str = field(default="quartet_analysis_summary_v1", init=False)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class QuartetAnalysisReportV1:
    parts: tuple[QuartetPartAlignmentV1, ...]
    shared_positions: tuple[QuartetSharedPositionSnapshotV1, ...]
    pairwise_asynchrony: tuple[QuartetPairwiseAsynchronyPointV1, ...]
    summary: QuartetAnalysisSummaryV1
    stale_after_s: float
    divergence_threshold_beats: float
    required_quorum_parts: int
    authority_boundary: str = field(
        default="quartet_multichannel_research_not_mixed_ensemble_authority",
        init=False,
    )
    schema_version: str = field(default="quartet_analysis_report_v1", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "authority_boundary": self.authority_boundary,
            "stale_after_s": self.stale_after_s,
            "divergence_threshold_beats": self.divergence_threshold_beats,
            "required_quorum_parts": self.required_quorum_parts,
            "summary": self.summary.to_dict(),
            "parts": [part.to_dict() for part in self.parts],
            "shared_positions": [snapshot.to_dict() for snapshot in self.shared_positions],
            "pairwise_asynchrony": [asdict(point) for point in self.pairwise_asynchrony],
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


class QuartetAnalyzer:
    """Research-only four-channel analyzer with independent per-part followers."""

    def __init__(
        self,
        parts: Iterable[QuartetPartInputV1],
        *,
        stale_after_s: float = 0.75,
        divergence_threshold_beats: float = 1.5,
        required_quorum_parts: int = 3,
        recovery_pause_gap_s: float = 1.5,
    ) -> None:
        self._parts = tuple(parts)
        if len(self._parts) != 4:
            raise ValueError("QuartetAnalyzer requires exactly four parts")
        for name, values in (
            ("part_id", [part.part_id for part in self._parts]),
            ("performer_id", [part.performer_id for part in self._parts]),
            ("channel_id", [part.channel_id for part in self._parts]),
        ):
            if len(set(values)) != 4:
                raise ValueError(f"quartet {name} values must be unique")
        if not isfinite(stale_after_s) or stale_after_s <= 0:
            raise ValueError("stale_after_s must be finite and > 0")
        if not isfinite(divergence_threshold_beats) or divergence_threshold_beats < 0:
            raise ValueError("divergence_threshold_beats must be finite and >= 0")
        if not 2 <= required_quorum_parts <= 4:
            raise ValueError("required_quorum_parts must be within [2, 4]")
        if not isfinite(recovery_pause_gap_s) or recovery_pause_gap_s <= 0:
            raise ValueError("recovery_pause_gap_s must be finite and > 0")
        self._stale_after_s = stale_after_s
        self._divergence_threshold_beats = divergence_threshold_beats
        self._required_quorum_parts = required_quorum_parts
        self._recovery_pause_gap_s = recovery_pause_gap_s

    def _run_part(self, part: QuartetPartInputV1) -> QuartetPartAlignmentV1:
        result = RecoveryAwareSymbolicFollower(
            part.score_events,
            pause_gap_s=self._recovery_pause_gap_s,
        ).run_events(part.observations)
        return QuartetPartAlignmentV1(
            part_id=part.part_id,
            performer_id=part.performer_id,
            channel_id=part.channel_id,
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
        parts: tuple[QuartetPartAlignmentV1, ...],
    ) -> tuple[QuartetSharedPositionSnapshotV1, ...]:
        part_by_id = {part.part_id: part for part in parts}
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
        snapshots: list[QuartetSharedPositionSnapshotV1] = []
        for sequence_id, (observed_at_s, part_id, score_beat) in enumerate(timeline):
            latest[part_id] = (score_beat, observed_at_s)
            positions: list[QuartetPartPositionV1] = []
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
                    QuartetPartPositionV1(
                        part_id=candidate_id,
                        channel_id=part_by_id[candidate_id].channel_id,
                        score_beat=candidate_beat,
                        last_update_s=candidate_time,
                        age_s=age_s,
                    )
                )
            coverage_ratio = len(positions) / len(parts)
            if len(positions) < self._required_quorum_parts:
                shared_score_beat = None
                spread_beats = None
                status = QuartetPositionStatus.INSUFFICIENT_QUORUM
            else:
                beats = [position.score_beat for position in positions]
                shared_score_beat = float(median(beats))
                spread_beats = max(beats) - min(beats)
                if spread_beats > self._divergence_threshold_beats:
                    status = QuartetPositionStatus.DIVERGENT
                elif len(positions) == len(parts):
                    status = QuartetPositionStatus.FULL_CONSENSUS
                else:
                    status = QuartetPositionStatus.QUORUM_CONSENSUS
            snapshots.append(
                QuartetSharedPositionSnapshotV1(
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
                    coverage_ratio=coverage_ratio,
                    spread_beats=spread_beats,
                    required_quorum_parts=self._required_quorum_parts,
                )
            )
        return tuple(snapshots)

    @staticmethod
    def _pairwise_asynchrony(
        parts: tuple[QuartetPartAlignmentV1, ...],
    ) -> tuple[QuartetPairwiseAsynchronyPointV1, ...]:
        points: list[QuartetPairwiseAsynchronyPointV1] = []
        for first, second in combinations(parts, 2):
            first_by_beat: dict[float, list[float]] = {}
            second_by_beat: dict[float, list[float]] = {}
            for match in first.matches:
                first_by_beat.setdefault(match.score_beat, []).append(match.observed_at_s)
            for match in second.matches:
                second_by_beat.setdefault(match.score_beat, []).append(match.observed_at_s)
            for score_beat in sorted(set(first_by_beat) & set(second_by_beat)):
                first_times = sorted(first_by_beat[score_beat])
                second_times = sorted(second_by_beat[score_beat])
                for occurrence_index, (first_time, second_time) in enumerate(
                    zip(first_times, second_times, strict=False)
                ):
                    signed_delta_ms = (second_time - first_time) * 1000.0
                    points.append(
                        QuartetPairwiseAsynchronyPointV1(
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

    def run(self) -> QuartetAnalysisReportV1:
        parts = tuple(self._run_part(part) for part in self._parts)
        snapshots = self._shared_snapshots(parts)
        pairwise = self._pairwise_asynchrony(parts)
        absolute_async = [point.absolute_delta_ms for point in pairwise]
        spread_values = [
            snapshot.spread_beats
            for snapshot in snapshots
            if snapshot.spread_beats is not None
        ]
        summary = QuartetAnalysisSummaryV1(
            part_count=4,
            channel_count=4,
            pair_count=6,
            snapshot_count=len(snapshots),
            full_consensus_snapshots=sum(
                snapshot.status is QuartetPositionStatus.FULL_CONSENSUS
                for snapshot in snapshots
            ),
            quorum_consensus_snapshots=sum(
                snapshot.status is QuartetPositionStatus.QUORUM_CONSENSUS
                for snapshot in snapshots
            ),
            divergent_snapshots=sum(
                snapshot.status is QuartetPositionStatus.DIVERGENT
                for snapshot in snapshots
            ),
            insufficient_quorum_snapshots=sum(
                snapshot.status is QuartetPositionStatus.INSUFFICIENT_QUORUM
                for snapshot in snapshots
            ),
            degraded_insufficient_quorum_snapshots=sum(
                snapshot.status is QuartetPositionStatus.INSUFFICIENT_QUORUM
                and not snapshot.unavailable_part_ids
                for snapshot in snapshots
            ),
            pairwise_asynchrony_points=len(pairwise),
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
            max_position_spread_beats=max(spread_values, default=0.0),
            max_stale_parts=max(
                (len(snapshot.stale_part_ids) for snapshot in snapshots),
                default=0,
            ),
            shared_confidence_available=False,
        )
        return QuartetAnalysisReportV1(
            parts=parts,
            shared_positions=snapshots,
            pairwise_asynchrony=pairwise,
            summary=summary,
            stale_after_s=self._stale_after_s,
            divergence_threshold_beats=self._divergence_threshold_beats,
            required_quorum_parts=self._required_quorum_parts,
        )
