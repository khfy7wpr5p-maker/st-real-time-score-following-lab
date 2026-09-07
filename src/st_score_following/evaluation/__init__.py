"""Evaluation helpers for reproducible score-following research."""

from .alignment_metrics import AlignmentMetrics, evaluate_expected_onsets
from .guitar import (
    GUITAR_EVENT_CLASSES,
    GUITAR_PITCH_SETS,
    guitar_category_indices,
    guitar_expected_onsets,
    guitar_note_level_events,
    guitar_score_events,
)
from .oracle_transcription import oracle_performance_events, synthetic_score_events
from .synthetic import SYNTHETIC_NOTES, write_quarter_note_midi

__all__ = [
    "AlignmentMetrics",
    "GUITAR_EVENT_CLASSES",
    "GUITAR_PITCH_SETS",
    "SYNTHETIC_NOTES",
    "evaluate_expected_onsets",
    "guitar_category_indices",
    "guitar_expected_onsets",
    "guitar_note_level_events",
    "guitar_score_events",
    "oracle_performance_events",
    "synthetic_score_events",
    "write_quarter_note_midi",
]
