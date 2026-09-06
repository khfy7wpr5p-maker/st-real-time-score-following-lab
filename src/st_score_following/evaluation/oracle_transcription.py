from __future__ import annotations

from st_score_following.contracts import ConfidenceV1, PerformanceEventV1
from st_score_following.symbolic import SymbolicScoreEvent

from .synthetic import SYNTHETIC_NOTES


def synthetic_score_events(
    *,
    notes: tuple[int, ...] = SYNTHETIC_NOTES,
) -> tuple[SymbolicScoreEvent, ...]:
    return tuple(
        SymbolicScoreEvent(score_beat=float(index), midi_pitches=(pitch,))
        for index, pitch in enumerate(notes)
    )


def oracle_performance_events(
    *,
    notes: tuple[int, ...] = SYNTHETIC_NOTES,
    bpm: float = 120.0,
    onset_offset_s: float = 0.0,
) -> tuple[PerformanceEventV1, ...]:
    """Build benchmark-only perfect symbolic observations; this is not an AMT model."""
    if bpm <= 0:
        raise ValueError("bpm must be > 0")
    if onset_offset_s < 0:
        raise ValueError("onset_offset_s must be >= 0")

    beat_duration_s = 60.0 / bpm
    confidence = ConfidenceV1(
        value=1.0,
        source="synthetic_oracle_ground_truth",
        calibrated=False,
        reason="Benchmark construction certainty; not transcription-model confidence.",
    )
    return tuple(
        PerformanceEventV1(
            event_id=f"oracle-{index}",
            observed_at_s=onset_offset_s + index * beat_duration_s,
            duration_s=beat_duration_s,
            midi_pitches=(pitch,),
            confidence=confidence,
        )
        for index, pitch in enumerate(notes)
    )
