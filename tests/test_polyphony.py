from st_score_following import ConfidenceV1, PerformanceEventV1
from st_score_following.polyphony import cluster_simultaneous_note_events


def _note(event_id: str, onset_s: float, pitch: int, duration_s: float = 0.4) -> PerformanceEventV1:
    return PerformanceEventV1(
        event_id=event_id,
        observed_at_s=onset_s,
        duration_s=duration_s,
        midi_pitches=(pitch,),
        confidence=ConfidenceV1(value=0.8, source="unit_test", calibrated=False),
    )


def test_cluster_groups_near_simultaneous_notes_and_preserves_arpeggio() -> None:
    clustered = cluster_simultaneous_note_events(
        (
            _note("a", 0.0, 52, 1.0),
            _note("b", 0.01, 55, 0.5),
            _note("c", 0.02, 59, 0.5),
            _note("d", 0.20, 64, 0.5),
        ),
        onset_tolerance_s=0.03,
    )

    assert len(clustered) == 2
    assert clustered[0].midi_pitches == (52, 55, 59)
    assert clustered[0].duration_s == 1.0
    assert clustered[0].confidence is not None
    assert clustered[0].confidence.value == 0.8
    assert clustered[1].midi_pitches == (64,)


def test_cluster_does_not_fabricate_confidence() -> None:
    event = PerformanceEventV1(
        event_id="unknown",
        observed_at_s=0.0,
        duration_s=0.5,
        midi_pitches=(60,),
        confidence=None,
    )
    clustered = cluster_simultaneous_note_events((event,))
    assert clustered[0].confidence is None
