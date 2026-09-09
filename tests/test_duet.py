import json

import pytest

from st_score_following import (
    DuetAnalyzer,
    DuetPartInputV1,
    PerformanceEventV1,
    SharedPositionStatus,
    SymbolicScoreEvent,
)

PART_A_PITCHES = (60, 62, 64, 65, 67, 69, 71, 72)
PART_B_PITCHES = (48, 50, 52, 53, 55, 57, 59, 60)


def _score(pitches: tuple[int, ...]) -> tuple[SymbolicScoreEvent, ...]:
    return tuple(
        SymbolicScoreEvent(score_beat=float(index), midi_pitches=(pitch,))
        for index, pitch in enumerate(pitches)
    )


def _events(
    prefix: str,
    pitches: tuple[int, ...],
    times: tuple[float, ...],
    indices: tuple[int, ...] | None = None,
) -> tuple[PerformanceEventV1, ...]:
    selected = tuple(range(len(pitches))) if indices is None else indices
    return tuple(
        PerformanceEventV1(
            event_id=f"{prefix}-{index}",
            observed_at_s=time,
            duration_s=None,
            midi_pitches=(pitches[index],),
            confidence=None,
        )
        for index, time in zip(selected, times, strict=True)
    )


def _part_a() -> DuetPartInputV1:
    return DuetPartInputV1(
        part_id="part-a",
        performer_id="performer-a",
        score_events=_score(PART_A_PITCHES),
        observations=_events(
            "a",
            PART_A_PITCHES,
            tuple(index * 0.5 for index in range(8)),
        ),
    )


def _part_b(
    *,
    indices: tuple[int, ...] | None = None,
    times: tuple[float, ...] | None = None,
) -> DuetPartInputV1:
    selected = tuple(range(8)) if indices is None else indices
    selected_times = (
        tuple(index * 0.5 + 0.02 for index in selected)
        if times is None
        else times
    )
    return DuetPartInputV1(
        part_id="part-b",
        performer_id="performer-b",
        score_events=_score(PART_B_PITCHES),
        observations=_events(
            "b",
            PART_B_PITCHES,
            selected_times,
            selected,
        ),
    )


def test_clean_duet_preserves_independent_parts_and_measures_asynchrony() -> None:
    report = DuetAnalyzer((_part_a(), _part_b())).run()

    assert [part.matched_events for part in report.parts] == [8, 8]
    assert [part.final_score_beat for part in report.parts] == [7.0, 7.0]
    assert report.summary.common_asynchrony_points == 8
    assert report.summary.mean_absolute_asynchrony_ms == pytest.approx(20.0)
    assert report.summary.max_absolute_asynchrony_ms == pytest.approx(20.0)
    assert report.summary.divergent_snapshots == 0
    assert not report.summary.shared_confidence_available


def test_dropped_part_b_event_does_not_block_part_a_following() -> None:
    report = DuetAnalyzer(
        (
            _part_a(),
            _part_b(indices=(0, 1, 2, 4, 5, 6, 7)),
        )
    ).run()

    part_a, part_b = report.parts
    assert part_a.matched_events == 8
    assert part_a.final_score_beat == 7.0
    assert part_b.matched_events == 7
    assert part_b.forward_skipped_score_events == 1
    assert report.summary.common_asynchrony_points == 7


def test_pause_makes_stale_part_explicit_while_other_part_keeps_progressing() -> None:
    report = DuetAnalyzer(
        (
            _part_a(),
            _part_b(
                times=(0.02, 0.52, 1.02, 3.02, 3.52, 4.02, 4.52, 5.02),
            ),
        ),
        stale_after_s=0.75,
    ).run()

    assert report.parts[0].matched_events == 8
    assert report.parts[1].pause_gaps == 1
    stale_snapshots = [
        snapshot
        for snapshot in report.shared_positions
        if "part-b" in snapshot.stale_part_ids
    ]
    assert stale_snapshots
    assert all(
        snapshot.status is SharedPositionStatus.SINGLE_PART
        for snapshot in stale_snapshots
    )
    assert all(
        "part-a" in snapshot.contributing_part_ids for snapshot in stale_snapshots
    )


def test_advanced_part_is_marked_divergent_without_overwriting_other_part() -> None:
    report = DuetAnalyzer(
        (
            _part_a(),
            _part_b(
                indices=(0, 1, 2, 5, 6, 7),
                times=(0.02, 0.52, 1.02, 1.52, 2.02, 2.52),
            ),
        ),
        divergence_threshold_beats=1.5,
    ).run()

    part_a, part_b = report.parts
    assert part_a.final_score_beat == 7.0
    assert part_b.forward_skipped_score_events == 2
    assert report.summary.divergent_snapshots >= 1
    divergent = [
        snapshot
        for snapshot in report.shared_positions
        if snapshot.status is SharedPositionStatus.DIVERGENT
    ]
    assert max(snapshot.spread_beats for snapshot in divergent) >= 2.0


def test_shared_snapshot_confidence_is_never_fabricated() -> None:
    report = DuetAnalyzer((_part_a(), _part_b())).run()

    assert report.shared_positions
    assert all(snapshot.confidence is None for snapshot in report.shared_positions)


def test_duet_requires_exactly_two_unique_parts_and_performers() -> None:
    with pytest.raises(ValueError, match="exactly two"):
        DuetAnalyzer((_part_a(),))

    duplicate_part = DuetPartInputV1(
        part_id="part-a",
        performer_id="performer-b",
        score_events=_score(PART_B_PITCHES),
        observations=_events(
            "b",
            PART_B_PITCHES,
            tuple(index * 0.5 + 0.02 for index in range(8)),
        ),
    )
    with pytest.raises(ValueError, match="part_id"):
        DuetAnalyzer((_part_a(), duplicate_part))


def test_json_export_keeps_duet_authority_boundary_explicit() -> None:
    report = DuetAnalyzer((_part_a(), _part_b())).run()
    data = json.loads(report.to_json())

    assert data["authority_boundary"] == "duet_research_not_ensemble_authority"
    assert data["summary"]["part_count"] == 2
    assert data["summary"]["shared_confidence_available"] is False
