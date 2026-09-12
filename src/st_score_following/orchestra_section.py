from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from math import isfinite
from typing import Any

from .orchestra_global import (
    OrchestraGlobalFollower,
    OrchestraGlobalMatchV1,
    OrchestraGlobalObservationV1,
    OrchestraGlobalReportV1,
    OrchestraGlobalScorePointV1,
)


class OrchestraSectionFamily(StrEnum):
    VIOLINS = "violins"
    STRINGS = "strings"
    WINDS = "winds"
    BRASS = "brass"


class OrchestraSectionFusionStatus(StrEnum):
    FULL_CONSENSUS = "full_consensus"
    QUORUM_CONSENSUS = "quorum_consensus"
    DIVERGENT = "divergent"
    INSUFFICIENT_QUORUM = "insufficient_quorum"


@dataclass(frozen=True, slots=True)
class OrchestraSectionInputV1:
    section_id: str
    family: OrchestraSectionFamily
    source_provenance: str
    score_points: tuple[OrchestraGlobalScorePointV1, ...]
    observations: tuple[OrchestraGlobalObservationV1, ...]
    schema_version: str = field(default="orchestra_section_input_v1", init=False)

    def __post_init__(self) -> None:
        if not self.section_id.strip():
            raise ValueError("section_id must be non-empty")
        if not self.source_provenance.strip():
            raise ValueError("source_provenance must be non-empty")
        if not self.score_points:
            raise ValueError("score_points must not be empty")


@dataclass(frozen=True, slots=True)
class OrchestraSectionAlignmentV1:
    section_id: str
    family: OrchestraSectionFamily
    source_provenance: str
    report: OrchestraGlobalReportV1
    schema_version: str = field(default="orchestra_section_alignment_v1", init=False)

    @property
    def matches(self) -> tuple[OrchestraGlobalMatchV1, ...]:
        return self.report.matches

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "section_id": self.section_id,
            "family": self.family.value,
            "source_provenance": self.source_provenance,
            "report": self.report.to_dict(),
        }


@dataclass(frozen=True, slots=True)
class OrchestraSectionPositionV1:
    section_id: str
    family: OrchestraSectionFamily
    score_index: int
    measure_index: int
    beat_in_measure: float
    score_beat: float
    last_update_s: float
    age_s: float
    schema_version: str = field(default="orchestra_section_position_v1", init=False)

    def __post_init__(self) -> None:
        if not self.section_id.strip():
            raise ValueError("section_id must be non-empty")
        if self.score_index < 0 or self.measure_index < 1:
            raise ValueError("score and measure indices must be non-negative/positive")
        for name, value in (
            ("beat_in_measure", self.beat_in_measure),
            ("score_beat", self.score_beat),
            ("last_update_s", self.last_update_s),
            ("age_s", self.age_s),
        ):
            if not isfinite(value) or value < 0:
                raise ValueError(f"{name} must be finite and >= 0")


@dataclass(frozen=True, slots=True)
class OrchestraSectionFusionSnapshotV1:
    sequence_id: int
    observed_at_s: float
    status: OrchestraSectionFusionStatus
    fused_score_index: int | None
    fused_measure_index: int | None
    fused_beat_in_measure: float | None
    fused_score_beat: float | None
    positions: tuple[OrchestraSectionPositionV1, ...]
    contributing_section_ids: tuple[str, ...]
    disagreeing_section_ids: tuple[str, ...]
    stale_section_ids: tuple[str, ...]
    unavailable_section_ids: tuple[str, ...]
    required_quorum_sections: int
    confidence: None = None
    schema_version: str = field(default="orchestra_section_fusion_snapshot_v1", init=False)

    def __post_init__(self) -> None:
        if self.sequence_id < 0:
            raise ValueError("sequence_id must be >= 0")
        if not isfinite(self.observed_at_s) or self.observed_at_s < 0:
            raise ValueError("observed_at_s must be finite and >= 0")
        fused_values = (
            self.fused_score_index,
            self.fused_measure_index,
            self.fused_beat_in_measure,
            self.fused_score_beat,
        )
        if self.status in {
            OrchestraSectionFusionStatus.DIVERGENT,
            OrchestraSectionFusionStatus.INSUFFICIENT_QUORUM,
        }:
            if any(value is not None for value in fused_values):
                raise ValueError("divergent/below-quorum snapshots must not publish fused position")
        elif any(value is None for value in fused_values):
            raise ValueError("consensus snapshots require a complete fused position")

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


@dataclass(frozen=True, slots=True)
class OrchestraSectionSummaryV1:
    section_count: int
    snapshot_count: int
    full_consensus_snapshots: int
    quorum_consensus_snapshots: int
    divergent_snapshots: int
    insufficient_quorum_snapshots: int
    outlier_section_snapshots: int
    fused_confidence_available: bool
    schema_version: str = field(default="orchestra_section_summary_v1", init=False)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class OrchestraSectionReportV1:
    sections: tuple[OrchestraSectionAlignmentV1, ...]
    snapshots: tuple[OrchestraSectionFusionSnapshotV1, ...]
    summary: OrchestraSectionSummaryV1
    stale_after_s: float
    required_quorum_sections: int
    authority_boundary: str = field(
        default="orchestra_section_fusion_research_not_acoustic_source_separation_authority",
        init=False,
    )
    schema_version: str = field(default="orchestra_section_report_v1", init=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "authority_boundary": self.authority_boundary,
            "stale_after_s": self.stale_after_s,
            "required_quorum_sections": self.required_quorum_sections,
            "summary": self.summary.to_dict(),
            "sections": [section.to_dict() for section in self.sections],
            "snapshots": [snapshot.to_dict() for snapshot in self.snapshots],
        }


class OrchestraSectionAnalyzer:
    """Research-only section fusion over independent global-position followers."""

    def __init__(
        self,
        sections: tuple[OrchestraSectionInputV1, ...],
        *,
        stale_after_s: float = 0.75,
        required_quorum_sections: int = 3,
    ) -> None:
        if len(sections) < 2:
            raise ValueError("at least two sections are required")
        if len({section.section_id for section in sections}) != len(sections):
            raise ValueError("section_id values must be unique")
        if len({section.family for section in sections}) != len(sections):
            raise ValueError("section families must be unique in this research analyzer")
        if not isfinite(stale_after_s) or stale_after_s <= 0:
            raise ValueError("stale_after_s must be finite and > 0")
        if not 2 <= required_quorum_sections <= len(sections):
            raise ValueError("required_quorum_sections must be within [2, section_count]")
        reference_grid = tuple(
            (point.score_index, point.measure_index, point.beat_in_measure, point.score_beat)
            for point in sections[0].score_points
        )
        for section in sections[1:]:
            grid = tuple(
                (point.score_index, point.measure_index, point.beat_in_measure, point.score_beat)
                for point in section.score_points
            )
            if grid != reference_grid:
                raise ValueError("all section score grids must share identical global identity")
        self._sections = sections
        self._stale_after_s = stale_after_s
        self._required_quorum_sections = required_quorum_sections

    def _align_sections(self) -> tuple[OrchestraSectionAlignmentV1, ...]:
        return tuple(
            OrchestraSectionAlignmentV1(
                section_id=section.section_id,
                family=section.family,
                source_provenance=section.source_provenance,
                report=OrchestraGlobalFollower(section.score_points).run(section.observations),
            )
            for section in self._sections
        )

    def _snapshots(
        self,
        alignments: tuple[OrchestraSectionAlignmentV1, ...],
    ) -> tuple[OrchestraSectionFusionSnapshotV1, ...]:
        alignment_by_id = {item.section_id: item for item in alignments}
        all_ids = tuple(item.section_id for item in alignments)
        timeline = sorted(
            (
                (match.observed_at_s, alignment.section_id, match)
                for alignment in alignments
                for match in alignment.matches
            ),
            key=lambda item: (item[0], item[1]),
        )
        latest: dict[str, OrchestraGlobalMatchV1] = {}
        snapshots: list[OrchestraSectionFusionSnapshotV1] = []
        for sequence_id, (observed_at_s, section_id, match) in enumerate(timeline):
            latest[section_id] = match
            positions: list[OrchestraSectionPositionV1] = []
            stale: list[str] = []
            unavailable: list[str] = []
            for candidate_id in all_ids:
                candidate = latest.get(candidate_id)
                if candidate is None:
                    unavailable.append(candidate_id)
                    continue
                age_s = observed_at_s - candidate.observed_at_s
                if age_s > self._stale_after_s:
                    stale.append(candidate_id)
                    continue
                alignment = alignment_by_id[candidate_id]
                positions.append(
                    OrchestraSectionPositionV1(
                        section_id=candidate_id,
                        family=alignment.family,
                        score_index=candidate.score_index,
                        measure_index=candidate.measure_index,
                        beat_in_measure=candidate.beat_in_measure,
                        score_beat=candidate.score_beat,
                        last_update_s=candidate.observed_at_s,
                        age_s=age_s,
                    )
                )

            fused_score_index: int | None = None
            fused_measure_index: int | None = None
            fused_beat_in_measure: float | None = None
            fused_score_beat: float | None = None
            contributing: tuple[str, ...] = ()
            disagreeing: tuple[str, ...] = ()
            if len(positions) < self._required_quorum_sections:
                status = OrchestraSectionFusionStatus.INSUFFICIENT_QUORUM
            else:
                counts = Counter(position.score_index for position in positions)
                best_index, best_count = counts.most_common(1)[0]
                if best_count < self._required_quorum_sections:
                    status = OrchestraSectionFusionStatus.DIVERGENT
                    disagreeing = tuple(position.section_id for position in positions)
                else:
                    agreeing = tuple(
                        position for position in positions if position.score_index == best_index
                    )
                    exemplar = agreeing[0]
                    fused_score_index = exemplar.score_index
                    fused_measure_index = exemplar.measure_index
                    fused_beat_in_measure = exemplar.beat_in_measure
                    fused_score_beat = exemplar.score_beat
                    contributing = tuple(position.section_id for position in agreeing)
                    disagreeing = tuple(
                        position.section_id
                        for position in positions
                        if position.score_index != best_index
                    )
                    status = (
                        OrchestraSectionFusionStatus.FULL_CONSENSUS
                        if best_count == len(all_ids) and len(positions) == len(all_ids)
                        else OrchestraSectionFusionStatus.QUORUM_CONSENSUS
                    )
            snapshots.append(
                OrchestraSectionFusionSnapshotV1(
                    sequence_id=sequence_id,
                    observed_at_s=observed_at_s,
                    status=status,
                    fused_score_index=fused_score_index,
                    fused_measure_index=fused_measure_index,
                    fused_beat_in_measure=fused_beat_in_measure,
                    fused_score_beat=fused_score_beat,
                    positions=tuple(positions),
                    contributing_section_ids=contributing,
                    disagreeing_section_ids=disagreeing,
                    stale_section_ids=tuple(stale),
                    unavailable_section_ids=tuple(unavailable),
                    required_quorum_sections=self._required_quorum_sections,
                )
            )
        return tuple(snapshots)

    def run(self) -> OrchestraSectionReportV1:
        alignments = self._align_sections()
        snapshots = self._snapshots(alignments)
        summary = OrchestraSectionSummaryV1(
            section_count=len(alignments),
            snapshot_count=len(snapshots),
            full_consensus_snapshots=sum(
                item.status is OrchestraSectionFusionStatus.FULL_CONSENSUS
                for item in snapshots
            ),
            quorum_consensus_snapshots=sum(
                item.status is OrchestraSectionFusionStatus.QUORUM_CONSENSUS
                for item in snapshots
            ),
            divergent_snapshots=sum(
                item.status is OrchestraSectionFusionStatus.DIVERGENT for item in snapshots
            ),
            insufficient_quorum_snapshots=sum(
                item.status is OrchestraSectionFusionStatus.INSUFFICIENT_QUORUM
                for item in snapshots
            ),
            outlier_section_snapshots=sum(bool(item.disagreeing_section_ids) for item in snapshots),
            fused_confidence_available=False,
        )
        return OrchestraSectionReportV1(
            sections=alignments,
            snapshots=snapshots,
            summary=summary,
            stale_after_s=self._stale_after_s,
            required_quorum_sections=self._required_quorum_sections,
        )
