from __future__ import annotations

from st_score_following import (
    OrchestraGlobalObservationV1,
    OrchestraGlobalScorePointV1,
    OrchestraSectionAnalyzer,
    OrchestraSectionFamily,
    OrchestraSectionFusionStatus,
    OrchestraSectionInputV1,
)

BASE = (
    (0, 4, 5, 7, 8),
    (0, 2, 5, 8, 11),
    (1, 2, 3, 5, 6),
    (1, 3, 6, 8, 9),
    (2, 3, 5, 9, 10),
    (3, 5, 7, 8, 10),
    (1, 3, 4, 8, 11),
    (2, 3, 7, 8, 10),
    (1, 4, 6, 9, 11),
    (1, 2, 4, 7, 9),
    (0, 1, 4, 6, 8),
    (4, 5, 7, 10, 11),
    (0, 3, 5, 6, 11),
    (0, 1, 4, 7, 9),
    (3, 4, 5, 9, 10),
    (0, 4, 7, 8, 9),
)
CONFIG = {
    "violins": (OrchestraSectionFamily.VIOLINS, 0, 0.000),
    "strings": (OrchestraSectionFamily.STRINGS, 2, 0.015),
    "winds": (OrchestraSectionFamily.WINDS, 5, 0.030),
    "brass": (OrchestraSectionFamily.BRASS, 7, 0.045),
}


def _texture(index: int, shift: int) -> tuple[int, ...]:
    return tuple(sorted({(value + shift) % 12 for value in BASE[index]}))


def _section(name: str, indices: tuple[int, ...] = tuple(range(16))) -> OrchestraSectionInputV1:
    family, shift, offset = CONFIG[name]
    score = tuple(
        OrchestraGlobalScorePointV1(
            score_index=index,
            measure_index=index // 4 + 1,
            beat_in_measure=float(index % 4 + 1),
            score_beat=float(index),
            texture_pitch_classes=_texture(index, shift),
        )
        for index in range(16)
    )
    observations = tuple(
        OrchestraGlobalObservationV1(
            event_id=f"{name}-{ordinal}-{score_index}",
            observed_at_s=ordinal * 0.5 + offset,
            texture_pitch_classes=_texture(score_index, shift),
            confidence=None,
        )
        for ordinal, score_index in enumerate(indices)
    )
    return OrchestraSectionInputV1(
        section_id=f"section-{name}",
        family=family,
        source_provenance=f"repository_fixture:{name}",
        score_points=score,
        observations=observations,
    )


def _all_sections(**overrides: tuple[int, ...]) -> tuple[OrchestraSectionInputV1, ...]:
    return tuple(_section(name, overrides.get(name, tuple(range(16)))) for name in CONFIG)


def test_clean_sections_preserve_independent_alignment_and_reach_full_consensus() -> None:
    report = OrchestraSectionAnalyzer(_all_sections()).run()

    assert all(len(section.matches) == 16 for section in report.sections)
    assert report.snapshots[-1].status is OrchestraSectionFusionStatus.FULL_CONSENSUS
    assert report.snapshots[-1].fused_score_index == 15
    assert report.summary.full_consensus_snapshots > 0
    assert report.summary.fused_confidence_available is False


def test_one_section_dropout_keeps_three_section_quorum_available() -> None:
    sections = _all_sections(strings=tuple(range(8)))
    report = OrchestraSectionAnalyzer(sections).run()

    assert report.sections[1].report.summary.matched_observations == 8
    assert report.snapshots[-1].status is OrchestraSectionFusionStatus.QUORUM_CONSENSUS
    assert report.snapshots[-1].fused_score_index == 15
    assert "section-strings" in report.snapshots[-1].stale_section_ids


def test_advancing_winds_are_exposed_as_outlier_without_overwriting_other_sections() -> None:
    advanced_winds = tuple(range(6)) + tuple(range(8, 16))
    report = OrchestraSectionAnalyzer(_all_sections(winds=advanced_winds)).run()

    assert report.sections[2].report.summary.forward_skipped_score_points == 2
    assert report.summary.outlier_section_snapshots > 0
    assert any(
        "section-winds" in snapshot.disagreeing_section_ids
        and snapshot.status is OrchestraSectionFusionStatus.QUORUM_CONSENSUS
        for snapshot in report.snapshots
    )
    assert report.snapshots[-1].fused_score_index == 15


def test_two_section_loss_becomes_insufficient_quorum_without_fabricated_position() -> None:
    stopped = tuple(range(6))
    report = OrchestraSectionAnalyzer(
        _all_sections(violins=stopped, strings=stopped)
    ).run()

    final = report.snapshots[-1]
    assert final.status is OrchestraSectionFusionStatus.INSUFFICIENT_QUORUM
    assert final.fused_score_index is None
    assert final.fused_measure_index is None
    assert final.confidence is None


def test_section_score_grids_must_share_global_identity() -> None:
    sections = list(_all_sections())
    brass = sections[-1]
    altered_score = list(brass.score_points)
    point = altered_score[3]
    altered_score[3] = OrchestraGlobalScorePointV1(
        score_index=point.score_index,
        measure_index=point.measure_index,
        beat_in_measure=point.beat_in_measure,
        score_beat=point.score_beat + 0.25,
        texture_pitch_classes=point.texture_pitch_classes,
    )
    sections[-1] = OrchestraSectionInputV1(
        section_id=brass.section_id,
        family=brass.family,
        source_provenance=brass.source_provenance,
        score_points=tuple(altered_score),
        observations=brass.observations,
    )

    try:
        OrchestraSectionAnalyzer(tuple(sections))
    except ValueError as exc:
        assert "global identity" in str(exc)
    else:
        raise AssertionError("mismatched section score grids must be rejected")
