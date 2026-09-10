import json

import pytest

from st_score_following import (
    InstrumentFamily,
    MixedEnsembleAnalyzer,
    MixedEnsemblePartInputV1,
    MixedPositionStatus,
    ObservationPathKind,
    ObservationTimingBasis,
    PerformanceEventV1,
    SymbolicScoreEvent,
)

PITCHES = {
    "piano": (60, 62, 64, 65, 67, 69, 71, 72),
    "guitar": (52, 54, 55, 57, 59, 60, 62, 64),
    "violin": (67, 69, 71, 72, 74, 76, 77, 79),
    "voice": (55, 57, 59, 60, 62, 64, 65, 67),
}
CONFIG = {
    "piano": (InstrumentFamily.PIANO, ObservationPathKind.DIRECT_MIDI, 0.0),
    "guitar": (InstrumentFamily.GUITAR, ObservationPathKind.TRANSCRIPTION_SYMBOLIC, 0.02),
    "violin": (InstrumentFamily.VIOLIN, ObservationPathKind.EXTERNAL_EVENT_ADAPTER, 0.035),
    "voice": (InstrumentFamily.VOICE, ObservationPathKind.SYNTHETIC_ORACLE, 0.05),
}


def _part(
    name: str,
    *,
    indices: tuple[int, ...] = tuple(range(8)),
    timing_basis: ObservationTimingBasis = ObservationTimingBasis.PERFORMANCE_ONSET,
    shift_after: int | None = None,
    shift_s: float = 0.0,
    use_score_time: bool = True,
) -> MixedEnsemblePartInputV1:
    family, path, offset = CONFIG[name]
    score = tuple(
        SymbolicScoreEvent(score_beat=float(index), midi_pitches=(pitch,))
        for index, pitch in enumerate(PITCHES[name])
    )
    observations = []
    for ordinal, score_index in enumerate(indices):
        base_index = score_index if use_score_time else ordinal
        observed_at_s = base_index * 0.5 + offset
        if shift_after is not None and score_index >= shift_after:
            observed_at_s += shift_s
        observations.append(
            PerformanceEventV1(
                event_id=f"{name}-{ordinal}-{score_index}",
                observed_at_s=observed_at_s,
                duration_s=0.2,
                midi_pitches=(PITCHES[name][score_index],),
                confidence=None,
            )
        )
    return MixedEnsemblePartInputV1(
        part_id=f"part-{name}",
        performer_id=f"performer-{name}",
        channel_id=f"channel-{name}",
        instrument_family=family,
        observation_path=path,
        timing_basis=timing_basis,
        path_source=f"repository_fixture:{path.value}",
        score_events=score,
        observations=tuple(observations),
    )


def _clean_parts() -> tuple[MixedEnsemblePartInputV1, ...]:
    return tuple(_part(name) for name in CONFIG)


def test_requires_heterogeneous_instrument_and_path_identity() -> None:
    with pytest.raises(ValueError, match="exactly four"):
        MixedEnsembleAnalyzer(_clean_parts()[:3])

    piano_parts = tuple(
        MixedEnsemblePartInputV1(
            part_id=part.part_id,
            performer_id=part.performer_id,
            channel_id=part.channel_id,
            instrument_family=InstrumentFamily.PIANO,
            observation_path=part.observation_path,
            timing_basis=part.timing_basis,
            path_source=part.path_source,
            score_events=part.score_events,
            observations=part.observations,
        )
        for part in _clean_parts()
    )
    with pytest.raises(ValueError, match="instrument families"):
        MixedEnsembleAnalyzer(piano_parts)


def test_clean_mixed_ensemble_preserves_four_independent_paths() -> None:
    report = MixedEnsembleAnalyzer(_clean_parts()).run()
    assert report.summary.instrument_family_count == 4
    assert report.summary.observation_path_count == 4
    assert all(part.matched_events == 8 for part in report.parts)
    assert all(part.final_score_beat == 7.0 for part in report.parts)
    assert report.summary.timing_comparable_parts == 4
    assert report.summary.timing_comparable_pair_count == 6
    assert report.summary.timing_abstained_pair_count == 0
    assert report.summary.pairwise_timing_points == 48
    assert report.summary.shared_confidence_available is False


def test_unverified_timing_path_abstains_without_blocking_score_following() -> None:
    parts = tuple(
        _part(name, timing_basis=ObservationTimingBasis.UNVERIFIED)
        if name == "voice"
        else _part(name)
        for name in CONFIG
    )
    report = MixedEnsembleAnalyzer(parts).run()
    by_id = {part.part_id: part for part in report.parts}
    assert by_id["part-voice"].matched_events == 8
    assert by_id["part-voice"].final_score_beat == 7.0
    assert report.summary.timing_comparable_parts == 3
    assert report.summary.timing_ineligible_parts == 1
    assert report.summary.timing_comparable_pair_count == 3
    assert report.summary.timing_abstained_pair_count == 3
    assert report.summary.pairwise_timing_points == 24
    assert all(
        "part-voice" in snapshot.timing_ineligible_part_ids
        for snapshot in report.shared_positions
    )
    assert report.summary.full_consensus_snapshots == 0
    assert report.summary.quorum_consensus_snapshots > 0


def test_unverified_path_plus_pause_can_drop_shared_position_below_quorum() -> None:
    parts = tuple(
        _part(name, timing_basis=ObservationTimingBasis.UNVERIFIED)
        if name == "voice"
        else _part(name, shift_after=4, shift_s=1.6)
        if name == "guitar"
        else _part(name)
        for name in CONFIG
    )
    report = MixedEnsembleAnalyzer(parts).run()
    by_id = {part.part_id: part for part in report.parts}
    assert by_id["part-guitar"].pause_gaps == 1
    assert by_id["part-voice"].matched_events == 8
    assert report.summary.degraded_insufficient_quorum_snapshots > 0
    degraded = [
        item
        for item in report.shared_positions
        if item.status is MixedPositionStatus.INSUFFICIENT_QUORUM
        and not item.unavailable_part_ids
    ]
    assert degraded
    assert all(item.shared_score_beat is None for item in degraded)


def test_dropped_event_is_localized_to_one_instrument_path() -> None:
    parts = tuple(
        _part(name, indices=(0, 1, 2, 4, 5, 6, 7))
        if name == "guitar"
        else _part(name)
        for name in CONFIG
    )
    report = MixedEnsembleAnalyzer(parts).run()
    by_id = {part.part_id: part for part in report.parts}
    assert by_id["part-piano"].matched_events == 8
    assert by_id["part-violin"].matched_events == 8
    assert by_id["part-voice"].matched_events == 8
    assert by_id["part-guitar"].matched_events == 7
    assert by_id["part-guitar"].forward_skipped_score_events == 1


def test_divergent_voice_path_is_not_forced_into_consensus() -> None:
    parts = tuple(
        _part(name, indices=(0, 1, 4, 5, 6, 7), use_score_time=False)
        if name == "voice"
        else _part(name)
        for name in CONFIG
    )
    report = MixedEnsembleAnalyzer(parts).run()
    by_id = {part.part_id: part for part in report.parts}
    assert by_id["part-voice"].forward_skipped_score_events == 2
    assert report.summary.divergent_snapshots > 0
    assert report.summary.max_position_spread_beats >= 2.0


def test_json_preserves_path_provenance_and_authority_boundary() -> None:
    parts = tuple(
        _part(name, timing_basis=ObservationTimingBasis.UNVERIFIED)
        if name == "violin"
        else _part(name)
        for name in CONFIG
    )
    payload = json.loads(MixedEnsembleAnalyzer(parts).run().to_json())
    assert (
        payload["authority_boundary"]
        == "mixed_ensemble_channel_separated_research_not_acoustic_mixture_authority"
    )
    violin = next(item for item in payload["parts"] if item["part_id"] == "part-violin")
    assert violin["instrument_family"] == "violin"
    assert violin["observation_path"] == "external_event_adapter"
    assert violin["timing_basis"] == "unverified"
    assert violin["timing_comparable"] is False
    assert payload["summary"]["shared_confidence_available"] is False
