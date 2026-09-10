from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from math import isfinite
from statistics import mean, median
from typing import Any

from .contracts import ConfidenceV1, PerformanceEventV1
from .ensemble import (
    QuartetAnalyzer,
    QuartetPartAlignmentV1,
    QuartetPartInputV1,
    QuartetPositionStatus,
)
from .recovery import RecoveryMatch
from .symbolic import SymbolicScoreEvent


class InstrumentFamily(StrEnum):
    PIANO = "piano"
    GUITAR = "guitar"
    VIOLIN = "violin"
    VOICE = "voice"


class ObservationPathKind(StrEnum):
    DIRECT_MIDI = "direct_midi"
    TRANSCRIPTION_SYMBOLIC = "transcription_symbolic"
    EXTERNAL_EVENT_ADAPTER = "external_event_adapter"
    SYNTHETIC_ORACLE = "synthetic_oracle"


class ObservationTimingBasis(StrEnum):
    PERFORMANCE_ONSET = "performance_onset"
    UNVERIFIED = "unverified"


class MixedPositionStatus(StrEnum):
    FULL_CONSENSUS = "full_consensus"
    QUORUM_CONSENSUS = "quorum_consensus"
    DIVERGENT = "divergent"
    INSUFFICIENT_QUORUM = "insufficient_quorum"


@dataclass(frozen=True, slots=True)
class MixedEnsemblePartInputV1:
    part_id: str
    performer_id: str
    channel_id: str
    instrument_family: InstrumentFamily
    observation_path: ObservationPathKind
    timing_basis: ObservationTimingBasis
    path_source: str
    score_events: tuple[SymbolicScoreEvent, ...]
    observations: tuple[PerformanceEventV1, ...]
    schema_version: str = field(default="mixed_ensemble_part_input_v1", init=False)

    def __post_init__(self) -> None:
        for name, value in (
            ("part_id", self.part_id),
            ("performer_id", self.performer_id),
            ("channel_id", self.channel_id),
            ("path_source", self.path_source),
        ):
            if not value.strip():
                raise ValueError(f"{name} must be non-empty")
        if not self.score_events:
            raise ValueError("score_events must not be empty")
        event_ids = [event.event_id for event in self.observations]
        if len(event_ids) != len(set(event_ids)):
            raise ValueError("observation event_id values must be unique within a part")
        for previous, current in zip(self.observations, self.observations[1:], strict=False):
            if current.observed_at_s < previous.observed_at_s:
                raise ValueError("observations must be ordered by observed_at_s")

    @property
    def timing_comparable(self) -> bool:
        return self.timing_basis is ObservationTimingBasis.PERFORMANCE_ONSET


@dataclass(frozen=True, slots=True)
class MixedEnsemblePartAlignmentV1:
    part_id: str
    performer_id: str
    channel_id: str
    instrument_family: InstrumentFamily
    observation_path: ObservationPathKind
    timing_basis: ObservationTimingBasis
    path_source: str
    alignment: QuartetPartAlignmentV1
    schema_version: str = field(default="mixed_ensemble_part_alignment_v1", init=False)

    @property
    def final_score_beat(self) -> float | None:
        return self.alignment.final_score_beat

    @property
    def matched_events(self) -> int:
        return self.alignment.matched_events

    @property
    def forward_skipped_score_events(self) -> int:
        return self.alignment.forward_skipped_score_events

    @property
    def pause_gaps(self) -> int:
        return self.alignment.pause_gaps

    @property
    def matches(self) -> tuple[RecoveryMatch, ...]:
        return self.alignment.matches

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "part_id": self.part_id,
            "performer_id": self.performer_id,
            "channel_id": self.channel_id,
            "instrument_family": self.instrument_family.value,
            "observation_path": self.observation_path.value,
            "timing_basis": self.timing_basis.value,
            "path_source": self.path_source,
            "timing_comparable": self.timing_basis is ObservationTimingBasis.PERFORMANCE_ONSET,
            "alignment": self.alignment.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class MixedPartPositionV1:
    part_id: str
    channel_id: str
    score_beat: float
    last_update_s: float
    age_s: float
    schema_version: str = field(default="mixed_part_position_v1", init=False)

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
class MixedSharedPositionSnapshotV1:
    sequence_id: int
    observed_at_s: float
    shared_score_beat: float | None
    status: MixedPositionStatus
    positions: tuple[MixedPartPositionV1, ...]
    contributing_part_ids: tuple[str, ...]
    stale_part_ids: tuple[str, ...]
    unavailable_part_ids: tuple[str, ...]
    timing_ineligible_part_ids: tuple[str, ...]
    coverage_ratio: float
    spread_beats: float | None
    required_quorum_parts: int
    confidence: ConfidenceV1 | None = None
    schema_version: str = field(default="mixed_shared_position_snapshot_v1", init=False)

    def __post_init__(self) -> None:
        if self.sequence_id < 0:
            raise ValueError("sequence_id must be >= 0")
        if not isfinite(self.observed_at_s) or self.observed_at_s < 0:
            raise ValueError("observed_at_s must be finite and >= 0")
        if not isfinite(self.coverage_ratio) or not 0 <= self.coverage_ratio <= 1:
            raise ValueError("coverage_ratio must be within [0, 1]")
        if len(self.positions) < self.required_quorum_parts:
            if self.status is not MixedPositionStatus.INSUFFICIENT_QUORUM:
                raise ValueError("below-quorum snapshot must be insufficient_quorum")
            if self.shared_score_beat is not None or self.spread_beats is not None:
                raise ValueError("below-quorum snapshot must not publish shared position")
        else:
            if self.status is MixedPositionStatus.INSUFFICIENT_QUORUM:
                raise ValueError("quorum snapshot cannot be insufficient_quorum")
            if self.shared_score_beat is None or self.spread_beats is None:
                raise ValueError("quorum snapshot must publish shared position and spread")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass(frozen=True, slots=True)
class MixedTimingAbstentionV1:
    first_part_id: str
    second_part_id: str
    reason: str
    schema_version: str = field(default="mixed_timing_abstention_v1", init=False)

    def __post_init__(self) -> None:
        if not self.first_part_id.strip() or not self.second_part_id.strip():
            raise ValueError("part IDs must be non-empty")
        if not self.reason.strip():
            raise ValueError("reason must be non-empty")


@dataclass(frozen=True, slots=True)
class MixedEnsembleSummaryV1:
    part_count: int
    instrument_family_count: int
    observation_path_count: int
    timing_comparable_parts: int
    timing_ineligible_parts: int
    timing_comparable_pair_count: int
    timing_abstained_pair_count: int
    pairwise_timing_points: int
    snapshot_count: int
    full_consensus_snapshots: int
    quorum_consensus_snapshots: int
    divergent_snapshots: int
    insufficient_quorum_snapshots: int
    degraded_insufficient_quorum_snapshots: int
    mean_absolute_asynchrony_ms: float | None
    max_absolute_asynchrony_ms: float | None
    max_position_spread_beats: float
    shared_confidence_available: bool
    schema_version: str = field(default="mixed_ensemble_summary_v1", init=False)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class MixedEnsembleReportV1:
    parts: tuple[MixedEnsemblePartAlignmentV1, ...]
    shared_positions: tuple[MixedSharedPositionSnapshotV1, ...]
    pairwise_timing: tuple[Any, ...]
    timing_abstentions: tuple[MixedTimingAbstentionV1, ...]
    summary: MixedEnsembleSummaryV1
    stale_after_s: float
    divergence_threshold_beats: float
    required_quorum_parts: int
    authority_boundary: str = field(
        default="mixed_ensemble_channel_separated_research_not_acoustic_mixture_authority",
        init=False,
    )
    schema_version: str = field(default="mixed_ensemble_report_v1", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "authority_boundary": self.authority_boundary,
            "stale_after_s": self.stale_after_s,
            "divergence_threshold_beats": self.divergence_threshold_beats,
            "required_quorum_parts": self.required_quorum_parts,
            "summary": self.summary.to_dict(),
            "parts": [part.to_dict() for part in self.parts],
            "shared_positions": [item.to_dict() for item in self.shared_positions],
            "pairwise_timing": [asdict(item) for item in self.pairwise_timing],
            "timing_abstentions": [asdict(item) for item in self.timing_abstentions],
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True, allow_nan=False)


class MixedEnsembleAnalyzer:
    """Four-source heterogeneous research analyzer with explicit timing eligibility."""

    def __init__(
        self,
        parts: tuple[MixedEnsemblePartInputV1, ...],
        *,
        stale_after_s: float = 0.75,
        divergence_threshold_beats: float = 1.5,
        required_quorum_parts: int = 3,
        recovery_pause_gap_s: float = 1.5,
    ) -> None:
        if len(parts) != 4:
            raise ValueError("MixedEnsembleAnalyzer requires exactly four parts")
        self._parts = parts
        for name, values in (
            ("part_id", [part.part_id for part in parts]),
            ("performer_id", [part.performer_id for part in parts]),
            ("channel_id", [part.channel_id for part in parts]),
        ):
            if len(set(values)) != 4:
                raise ValueError(f"mixed ensemble {name} values must be unique")
        if len({part.instrument_family for part in parts}) < 2:
            raise ValueError("mixed ensemble requires at least two instrument families")
        if len({part.observation_path for part in parts}) < 2:
            raise ValueError("mixed ensemble requires at least two observation paths")
        if not isfinite(stale_after_s) or stale_after_s <= 0:
            raise ValueError("stale_after_s must be finite and > 0")
        if not isfinite(divergence_threshold_beats) or divergence_threshold_beats < 0:
            raise ValueError("divergence_threshold_beats must be finite and >= 0")
        if not 2 <= required_quorum_parts <= 4:
            raise ValueError("required_quorum_parts must be within [2, 4]")
        self._stale_after_s = stale_after_s
        self._divergence_threshold_beats = divergence_threshold_beats
        self._required_quorum_parts = required_quorum_parts
        self._recovery_pause_gap_s = recovery_pause_gap_s

    def _run_quartet(self):
        quartet_parts = tuple(
            QuartetPartInputV1(
                part_id=part.part_id,
                performer_id=part.performer_id,
                channel_id=part.channel_id,
                score_events=part.score_events,
                observations=part.observations,
            )
            for part in self._parts
        )
        return QuartetAnalyzer(
            quartet_parts,
            stale_after_s=self._stale_after_s,
            divergence_threshold_beats=self._divergence_threshold_beats,
            required_quorum_parts=self._required_quorum_parts,
            recovery_pause_gap_s=self._recovery_pause_gap_s,
        ).run()

    def _shared_positions(
        self,
        parts: tuple[MixedEnsemblePartAlignmentV1, ...],
    ) -> tuple[MixedSharedPositionSnapshotV1, ...]:
        all_ids = tuple(part.part_id for part in parts)
        eligible_ids = tuple(
            part.part_id
            for part in parts
            if part.timing_basis is ObservationTimingBasis.PERFORMANCE_ONSET
        )
        ineligible_ids = tuple(part_id for part_id in all_ids if part_id not in eligible_ids)
        part_by_id = {part.part_id: part for part in parts}
        timeline = sorted(
            (
                (match.observed_at_s, part.part_id, match.score_beat)
                for part in parts
                if part.part_id in eligible_ids
                for match in part.matches
            ),
            key=lambda item: (item[0], item[1]),
        )
        latest: dict[str, tuple[float, float]] = {}
        snapshots: list[MixedSharedPositionSnapshotV1] = []
        for sequence_id, (observed_at_s, part_id, score_beat) in enumerate(timeline):
            latest[part_id] = (score_beat, observed_at_s)
            positions: list[MixedPartPositionV1] = []
            stale: list[str] = []
            unavailable: list[str] = []
            for candidate_id in eligible_ids:
                value = latest.get(candidate_id)
                if value is None:
                    unavailable.append(candidate_id)
                    continue
                candidate_beat, candidate_time = value
                age_s = observed_at_s - candidate_time
                if age_s > self._stale_after_s:
                    stale.append(candidate_id)
                    continue
                positions.append(
                    MixedPartPositionV1(
                        part_id=candidate_id,
                        channel_id=part_by_id[candidate_id].channel_id,
                        score_beat=candidate_beat,
                        last_update_s=candidate_time,
                        age_s=age_s,
                    )
                )
            if len(positions) < self._required_quorum_parts:
                status = MixedPositionStatus.INSUFFICIENT_QUORUM
                shared_score_beat = None
                spread_beats = None
            else:
                beats = [position.score_beat for position in positions]
                shared_score_beat = float(median(beats))
                spread_beats = max(beats) - min(beats)
                if spread_beats > self._divergence_threshold_beats:
                    status = MixedPositionStatus.DIVERGENT
                elif len(positions) == len(all_ids):
                    status = MixedPositionStatus.FULL_CONSENSUS
                else:
                    status = MixedPositionStatus.QUORUM_CONSENSUS
            snapshots.append(
                MixedSharedPositionSnapshotV1(
                    sequence_id=sequence_id,
                    observed_at_s=observed_at_s,
                    shared_score_beat=shared_score_beat,
                    status=status,
                    positions=tuple(positions),
                    contributing_part_ids=tuple(item.part_id for item in positions),
                    stale_part_ids=tuple(stale),
                    unavailable_part_ids=tuple(unavailable),
                    timing_ineligible_part_ids=ineligible_ids,
                    coverage_ratio=len(positions) / len(all_ids),
                    spread_beats=spread_beats,
                    required_quorum_parts=self._required_quorum_parts,
                )
            )
        return tuple(snapshots)

    def run(self) -> MixedEnsembleReportV1:
        quartet = self._run_quartet()
        metadata = {part.part_id: part for part in self._parts}
        parts = tuple(
            MixedEnsemblePartAlignmentV1(
                part_id=aligned.part_id,
                performer_id=aligned.performer_id,
                channel_id=aligned.channel_id,
                instrument_family=metadata[aligned.part_id].instrument_family,
                observation_path=metadata[aligned.part_id].observation_path,
                timing_basis=metadata[aligned.part_id].timing_basis,
                path_source=metadata[aligned.part_id].path_source,
                alignment=aligned,
            )
            for aligned in quartet.parts
        )
        eligible = {
            part.part_id
            for part in parts
            if part.timing_basis is ObservationTimingBasis.PERFORMANCE_ONSET
        }
        pairwise = tuple(
            point
            for point in quartet.pairwise_asynchrony
            if point.first_part_id in eligible and point.second_part_id in eligible
        )
        all_pairs = {
            tuple(sorted((first.part_id, second.part_id)))
            for index, first in enumerate(parts)
            for second in parts[index + 1 :]
        }
        comparable_pairs = {
            tuple(sorted((point.first_part_id, point.second_part_id))) for point in pairwise
        }
        abstentions = tuple(
            MixedTimingAbstentionV1(
                first_part_id=first,
                second_part_id=second,
                reason="pair timing abstained because at least one observation path lacks verified performance-onset timing",
            )
            for first, second in sorted(all_pairs - comparable_pairs)
        )
        snapshots = self._shared_positions(parts)
        abs_async = [point.absolute_delta_ms for point in pairwise]
        spread_values = [
            snapshot.spread_beats
            for snapshot in snapshots
            if snapshot.spread_beats is not None
        ]
        summary = MixedEnsembleSummaryV1(
            part_count=4,
            instrument_family_count=len({part.instrument_family for part in parts}),
            observation_path_count=len({part.observation_path for part in parts}),
            timing_comparable_parts=len(eligible),
            timing_ineligible_parts=4 - len(eligible),
            timing_comparable_pair_count=len(comparable_pairs),
            timing_abstained_pair_count=len(abstentions),
            pairwise_timing_points=len(pairwise),
            snapshot_count=len(snapshots),
            full_consensus_snapshots=sum(
                item.status is MixedPositionStatus.FULL_CONSENSUS for item in snapshots
            ),
            quorum_consensus_snapshots=sum(
                item.status is MixedPositionStatus.QUORUM_CONSENSUS for item in snapshots
            ),
            divergent_snapshots=sum(
                item.status is MixedPositionStatus.DIVERGENT for item in snapshots
            ),
            insufficient_quorum_snapshots=sum(
                item.status is MixedPositionStatus.INSUFFICIENT_QUORUM for item in snapshots
            ),
            degraded_insufficient_quorum_snapshots=sum(
                item.status is MixedPositionStatus.INSUFFICIENT_QUORUM
                and not item.unavailable_part_ids
                for item in snapshots
            ),
            mean_absolute_asynchrony_ms=mean(abs_async) if abs_async else None,
            max_absolute_asynchrony_ms=max(abs_async) if abs_async else None,
            max_position_spread_beats=max(spread_values, default=0.0),
            shared_confidence_available=False,
        )
        return MixedEnsembleReportV1(
            parts=parts,
            shared_positions=snapshots,
            pairwise_timing=pairwise,
            timing_abstentions=abstentions,
            summary=summary,
            stale_after_s=self._stale_after_s,
            divergence_threshold_beats=self._divergence_threshold_beats,
            required_quorum_parts=self._required_quorum_parts,
        )
