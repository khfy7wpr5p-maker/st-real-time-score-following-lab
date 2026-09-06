import pytest

from st_score_following import (
    AlignmentV1,
    ConfidenceV1,
    ObservationKind,
    ObservationV1,
    PerformanceEventV1,
    ScorePositionV1,
    TempoStateV1,
)


def confidence(value: float = 0.8) -> ConfidenceV1:
    return ConfidenceV1(value=value, source="test")


def test_score_position_serializes_schema() -> None:
    position = ScorePositionV1(measure_index=4, beat=2.5, score_time_s=12.0)
    assert position.to_dict()["schema_version"] == "score_position_v1"


def test_confidence_rejects_out_of_range() -> None:
    with pytest.raises(ValueError):
        confidence(1.1)


def test_observation_serializes_enum_value() -> None:
    observation = ObservationV1(
        observation_id="obs-1",
        sequence_id=0,
        observed_at_s=0.1,
        kind=ObservationKind.MIDI_EVENT,
        payload={"pitch": 60},
    )
    assert observation.to_dict()["kind"] == "midi_event"


def test_tempo_requires_positive_bpm() -> None:
    with pytest.raises(ValueError):
        TempoStateV1(bpm=0, beat_phase=0, observed_at_s=0, confidence=confidence())


def test_alignment_exposes_signed_deviation() -> None:
    alignment = AlignmentV1(
        score_event_id="s1",
        observation_id="o1",
        score_time_s=1.0,
        performance_time_s=1.125,
        confidence=confidence(),
    )
    assert alignment.deviation_s == pytest.approx(0.125)


def test_performance_event_rejects_invalid_midi_pitch() -> None:
    with pytest.raises(ValueError):
        PerformanceEventV1(
            event_id="p1",
            observed_at_s=0,
            duration_s=0.5,
            midi_pitches=(128,),
            confidence=confidence(),
        )
