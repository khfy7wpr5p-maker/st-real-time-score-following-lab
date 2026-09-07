from __future__ import annotations

from ..contracts import ConfidenceV1, PerformanceEventV1
from ..symbolic import SymbolicScoreEvent

GUITAR_PITCH_SETS = (
    (40, 52, 55, 59, 64),
    (55,),
    (59,),
    (64,),
    (36, 48, 52, 55, 60),
    (52,),
    (55,),
    (60,),
    (38, 50, 54, 57, 60),
    (54,),
    (57,),
    (60,),
    (43, 47, 50, 55, 59),
    (47,),
    (50,),
    (55,),
)

GUITAR_EVENT_CLASSES = tuple(
    "chord_onset" if index % 4 == 0 else "arpeggio_under_sustain"
    for index in range(len(GUITAR_PITCH_SETS))
)


def guitar_score_events() -> tuple[SymbolicScoreEvent, ...]:
    return tuple(
        SymbolicScoreEvent(score_beat=float(index), midi_pitches=pitches)
        for index, pitches in enumerate(GUITAR_PITCH_SETS)
    )


def guitar_expected_onsets() -> tuple[tuple[float, float], ...]:
    return tuple((float(index), index * 0.5) for index in range(len(GUITAR_PITCH_SETS)))


def guitar_note_level_events() -> tuple[PerformanceEventV1, ...]:
    events: list[PerformanceEventV1] = []
    for index, pitches in enumerate(GUITAR_PITCH_SETS):
        onset_s = index * 0.5
        for pitch_index, pitch in enumerate(pitches):
            is_measure_bass = index % 4 == 0 and pitch_index == 0
            duration_s = 2.0 if is_measure_bass else 0.45
            events.append(
                PerformanceEventV1(
                    event_id=f"guitar-{index:02d}-{pitch_index:02d}",
                    observed_at_s=onset_s,
                    duration_s=duration_s,
                    midi_pitches=(pitch,),
                    confidence=ConfidenceV1(
                        value=1.0,
                        source="synthetic_guitar_oracle",
                        calibrated=False,
                        reason="Synthetic upper-bound event; not AMT model confidence.",
                    ),
                )
            )
    return tuple(events)


def guitar_category_indices() -> dict[str, tuple[int, ...]]:
    return {
        "chord_onsets": tuple(
            index for index, label in enumerate(GUITAR_EVENT_CLASSES) if label == "chord_onset"
        ),
        "arpeggio_under_sustain": tuple(
            index
            for index, label in enumerate(GUITAR_EVENT_CLASSES)
            if label == "arpeggio_under_sustain"
        ),
    }
