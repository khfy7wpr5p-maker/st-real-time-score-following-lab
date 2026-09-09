import json

import pytest

from st_score_following import (
    PerformanceEventV1,
    QuartetAnalyzer,
    QuartetPartInputV1,
    QuartetPositionStatus,
    SymbolicScoreEvent,
)

PART_PITCHES = {
    "part-a": (60, 62, 64, 65, 67, 69, 71, 72),
    "part-b": (48, 50, 52, 53, 55, 57, 59, 60),
    "part-c": (55, 57, 59, 60, 62, 64, 65, 67),
    "part-d": (72, 71, 69, 67, 65, 64, 62, 60),
}
OFFSETS = {"part-a": 0.0, "part-b": 0.02, "part-c": 0.035, "part-d": 0.05}


def _score(part_id: str) -> tuple[SymbolicScoreEvent, ...]:
    return tuple(
        SymbolicScoreEvent(score_beat=float(index), midi_pitches=(pitch,))
        for index, pitch in enumerate(PART_PITCHES[part_id])
    )


def _observations(
    part_id: str,
    score_indices: tuple[int, ...],
    *,
    use_score_time: bool = True,
    shift_after_score_index: int | None = None,
    shift_s: float = 0.0,
) -> tuple[PerformanceEventV1, ...]:
    events: list[PerformanceEventV1] = []
    for ordinal, score_index in enumerate(score_indices):
        base_index = score_index if use_score_time else ordinal
        observed_at_s = base_index * 0.5 + OFFSETS[part_id]
        if shift_after_score_index is not None and score_index >= shift_after_score_index:
            observed_at_s += shift_s
        events.append(
            PerformanceEventV1(
                event_id=f"{part_id}-{ordinal}-{score_index}",
                observed_at_s=observed_at_s,
                duration_s=0.2,
                midi_pitches=(PART_PITCHES[part_id][score_index],),
                confidence=None,
            )
        )
    return tuple(events)


def _part(
    part_id: str,
    score_indices: tuple[int, ...] = tuple(range(8)),
    *,
    use_score_time: bool = True,
    shift_after_score_index: int | None = None,
    shift_s: float = 0.0,
) -> QuartetPartInputV1:
    suffix = part_id[-1]
    return QuartetPartInputV1(
        part_id=part_id,
        performer_id=f"performer-{suffix}",
        channel_id=f"channel-{suffix}",
        score_events=_score(part_id),
        observations=_observations(
            part_id,
            score_indices,
            use_score_time=use_score_time,
            shift_after_score_index=shift_after_score_index,
            shift_s=shift_s,
        ),
    )


def _clean_parts() -> tuple[QuartetPartInputV1, ...]:
    return tuple(_part(part_id) for part_id in PART_PITCHES)


def test_quartet_requires_exactly_four_unique_parts_performers_and_channels() -> None:
    with pytest.raises(ValueError, match="exactly four"):
        QuartetAnalyzer(_clean_parts()[:3])

    parts = list(_clean_parts())
    duplicate = parts[3]
    parts[3] = QuartetPartInputV1(
        part_id=duplicate.part_id,
        performer_id=parts[0].performer_id,
        channel_id=duplicate.channel_id,
        score_events=duplicate.score_events,
        observations=duplicate.observations,
    )
    with pytest.raises(ValueError, match="performer_id"):
        QuartetAnalyzer(parts)


def test_quorum_validation_is_explicit() -> None:
    with pytest.raises(ValueError, match="within"):
        QuartetAnalyzer(_clean_parts(), required_quorum_parts=1)
    with pytest.raises(ValueError, match="within"):
        QuartetAnalyzer(_clean_parts(), required_quorum_parts=5)


def test_clean_quartet_preserves_independent_part_alignment() -> None:
    report = QuartetAnalyzer(_clean_parts()).run()
    assert len(report.parts) == 4
    assert all(part.matched_events == 8 for part in report.parts)
    assert all(part.final_score_beat == 7.0 for part in report.parts)
    assert report.summary.part_count == 4
    assert report.summary.channel_count == 4
    assert report.summary.pair_count == 6
    assert report.summary.pairwise_asynchrony_points == 48
    assert report.summary.divergent_snapshots == 0
    assert report.summary.degraded_insufficient_quorum_snapshots == 0
    assert report.summary.shared_confidence_available is False
    assert report.summary.max_absolute_asynchrony_ms == pytest.approx(50.0)


def test_dropped_event_is_localized_to_affected_part() -> None:
    parts = tuple(
        _part(part_id, tuple(index for index in range(8) if index != 3))
        if part_id == "part-d"
        else _part(part_id)
        for part_id in PART_PITCHES
    )
    report = QuartetAnalyzer(parts).run()
    by_id = {part.part_id: part for part in report.parts}
    assert by_id["part-a"].matched_events == 8
    assert by_id["part-b"].matched_events == 8
    assert by_id["part-c"].matched_events == 8
    assert by_id["part-d"].matched_events == 7
    assert by_id["part-d"].forward_skipped_score_events == 1
    assert all(part.final_score_beat == 7.0 for part in report.parts)


def test_pause_exposes_staleness_without_blocking_other_parts() -> None:
    parts = tuple(
        _part(
            part_id,
            shift_after_score_index=4,
            shift_s=1.6,
        )
        if part_id == "part-c"
        else _part(part_id)
        for part_id in PART_PITCHES
    )
    report = QuartetAnalyzer(parts).run()
    by_id = {part.part_id: part for part in report.parts}
    assert by_id["part-c"].pause_gaps == 1
    assert by_id["part-a"].matched_events == 8
    assert by_id["part-b"].matched_events == 8
    assert by_id["part-d"].matched_events == 8
    assert any("part-c" in snapshot.stale_part_ids for snapshot in report.shared_positions)
    assert report.summary.max_stale_parts >= 1


def test_advance_exposes_divergence_and_forward_skips() -> None:
    parts = tuple(
        _part(part_id, (0, 1, 4, 5, 6, 7), use_score_time=False)
        if part_id == "part-d"
        else _part(part_id)
        for part_id in PART_PITCHES
    )
    report = QuartetAnalyzer(parts).run()
    by_id = {part.part_id: part for part in report.parts}
    assert by_id["part-a"].matched_events == 8
    assert by_id["part-d"].forward_skipped_score_events == 2
    assert report.summary.divergent_snapshots > 0
    assert report.summary.max_position_spread_beats >= 2.0


def test_two_channel_loss_drops_shared_position_below_quorum() -> None:
    parts = tuple(
        _part(part_id, (0, 1, 2))
        if part_id in {"part-c", "part-d"}
        else _part(part_id)
        for part_id in PART_PITCHES
    )
    report = QuartetAnalyzer(parts).run()
    by_id = {part.part_id: part for part in report.parts}
    assert by_id["part-a"].matched_events == 8
    assert by_id["part-b"].matched_events == 8
    assert by_id["part-c"].final_score_beat == 2.0
    assert by_id["part-d"].final_score_beat == 2.0
    assert report.summary.degraded_insufficient_quorum_snapshots > 0
    degraded = [
        snapshot
        for snapshot in report.shared_positions
        if snapshot.status is QuartetPositionStatus.INSUFFICIENT_QUORUM
        and not snapshot.unavailable_part_ids
    ]
    assert degraded
    assert all(snapshot.shared_score_beat is None for snapshot in degraded)
    assert all(snapshot.spread_beats is None for snapshot in degraded)


def test_report_json_preserves_authority_boundary_and_missing_shared_confidence() -> None:
    report = QuartetAnalyzer(_clean_parts()).run()
    payload = json.loads(report.to_json())
    assert (
        payload["authority_boundary"]
        == "quartet_multichannel_research_not_mixed_ensemble_authority"
    )
    assert payload["summary"]["shared_confidence_available"] is False
    assert payload["required_quorum_parts"] == 3
