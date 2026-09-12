from __future__ import annotations

from st_score_following import (
    ConfidenceV1,
    OrchestraGlobalFollower,
    OrchestraGlobalObservationV1,
    OrchestraGlobalScorePointV1,
)

SIGNATURES = (
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


def _score() -> tuple[OrchestraGlobalScorePointV1, ...]:
    return tuple(
        OrchestraGlobalScorePointV1(
            score_index=index,
            measure_index=index // 4 + 1,
            beat_in_measure=float(index % 4 + 1),
            score_beat=float(index),
            texture_pitch_classes=signature,
        )
        for index, signature in enumerate(SIGNATURES)
    )


def _observation(index: int, at_s: float, signature: tuple[int, ...] | None = None):
    return OrchestraGlobalObservationV1(
        event_id=f"event-{index}-{at_s}",
        observed_at_s=at_s,
        texture_pitch_classes=SIGNATURES[index] if signature is None else signature,
        confidence=None,
    )


def test_tracks_global_measure_and_beat_without_instrument_identity() -> None:
    report = OrchestraGlobalFollower(_score()).run(
        _observation(index, index * 0.5) for index in range(len(SIGNATURES))
    )

    assert [match.score_index for match in report.matches] == list(range(len(SIGNATURES)))
    assert report.matches[7].measure_index == 2
    assert report.matches[7].beat_in_measure == 4.0
    assert report.summary.unmatched_observations == 0
    assert report.summary.confidence_available_matches == 0
    assert (
        report.authority_boundary
        == "global_measure_beat_research_not_per_instrument_transcription_authority"
    )


def test_dense_texture_proxy_tolerates_one_drop_and_one_extra_pitch_class() -> None:
    observations = []
    for index, signature in enumerate(SIGNATURES):
        values = set(signature)
        values.remove(signature[index % len(signature)])
        extra = (index * 7 + 3) % 12
        while extra in values:
            extra = (extra + 1) % 12
        values.add(extra)
        observations.append(_observation(index, index * 0.5, tuple(sorted(values))))

    report = OrchestraGlobalFollower(_score()).run(observations)

    assert [match.score_index for match in report.matches] == list(range(len(SIGNATURES)))
    assert min(match.texture_similarity for match in report.matches) >= 0.5


def test_restart_after_pause_relocks_globally() -> None:
    sequence = list(range(12)) + list(range(6))
    observations = []
    at_s = 0.0
    for ordinal, score_index in enumerate(sequence):
        if ordinal == 12:
            at_s += 2.0
        observations.append(_observation(score_index, at_s))
        at_s += 0.5

    report = OrchestraGlobalFollower(_score()).run(observations)

    assert [match.score_index for match in report.matches] == sequence
    assert report.summary.pause_gaps == 1
    assert report.summary.restart_relocks == 1
    assert report.summary.global_relocks == 1


def test_backward_jump_is_recovered_with_bounded_search() -> None:
    sequence = list(range(16)) + list(range(6, 12))
    report = OrchestraGlobalFollower(_score()).run(
        _observation(score_index, ordinal * 0.5)
        for ordinal, score_index in enumerate(sequence)
    )

    assert [match.score_index for match in report.matches] == sequence
    assert report.summary.backward_jumps == 1


def test_positive_confidence_gate_abstains_when_confidence_is_unavailable() -> None:
    follower = OrchestraGlobalFollower(_score(), min_observation_confidence=0.5)
    report = follower.run([_observation(0, 0.0)])

    assert report.summary.matched_observations == 0
    assert report.summary.unavailable_confidence_rejections == 1

    accepted = OrchestraGlobalObservationV1(
        event_id="confident",
        observed_at_s=0.0,
        texture_pitch_classes=SIGNATURES[0],
        confidence=ConfidenceV1(
            value=0.8,
            source="test_fixture",
            calibrated=False,
            reason="unit-test provenance only",
        ),
    )
    report = follower.run([accepted])
    assert report.summary.matched_observations == 1
    assert report.matches[0].confidence == 0.8
