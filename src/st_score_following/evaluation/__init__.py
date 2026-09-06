"""Evaluation helpers for reproducible score-following research."""

from .alignment_metrics import AlignmentMetrics, evaluate_expected_onsets
from .oracle_transcription import oracle_performance_events, synthetic_score_events
from .synthetic import SYNTHETIC_NOTES, write_quarter_note_midi

__all__ = [
    "AlignmentMetrics",
    "SYNTHETIC_NOTES",
    "evaluate_expected_onsets",
    "oracle_performance_events",
    "synthetic_score_events",
    "write_quarter_note_midi",
]
