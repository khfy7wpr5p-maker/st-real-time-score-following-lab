from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from math import isfinite
from time import perf_counter

from .contracts import PerformanceEventV1
from .followers.base import AlignmentPoint, FollowerRunResult, FollowerUpdate


@dataclass(frozen=True, slots=True)
class SymbolicScoreEvent:
    score_beat: float
    midi_pitches: tuple[int, ...]

    def __post_init__(self) -> None:
        if not isfinite(self.score_beat) or self.score_beat < 0:
            raise ValueError("score_beat must be finite and >= 0")
        if not self.midi_pitches:
            raise ValueError("midi_pitches must not be empty")
        if any(pitch < 0 or pitch > 127 for pitch in self.midi_pitches):
            raise ValueError("midi pitches must be within [0, 127]")


class CausalSymbolicFollower:
    """Forward-only pitch-event baseline for transcription-to-symbolic research."""

    backend_name = "st-symbolic-causal"
    backend_version = "0.1.0"

    def __init__(
        self,
        score_events: Iterable[SymbolicScoreEvent],
        *,
        lookahead_events: int = 2,
        min_event_confidence: float = 0.0,
    ) -> None:
        self._score_events = tuple(score_events)
        if not self._score_events:
            raise ValueError("score_events must not be empty")
        if lookahead_events < 0:
            raise ValueError("lookahead_events must be >= 0")
        if not 0.0 <= min_event_confidence <= 1.0:
            raise ValueError("min_event_confidence must be within [0, 1]")
        self._lookahead_events = lookahead_events
        self._min_event_confidence = min_event_confidence

    @staticmethod
    def _pitch_key(pitches: tuple[int, ...]) -> tuple[int, ...]:
        return tuple(sorted(set(pitches)))

    def run_events(self, events: Iterable[PerformanceEventV1]) -> FollowerRunResult:
        started = perf_counter()
        cursor = 0
        matched = 0
        unmatched = 0
        skipped_score_events = 0
        low_confidence_rejections = 0
        unavailable_confidence = 0
        unavailable_confidence_rejections = 0
        updates: list[FollowerUpdate] = []
        alignment_path: list[AlignmentPoint] = []

        for event in events:
            event_confidence = event.confidence
            if event_confidence is None:
                unavailable_confidence += 1
                if self._min_event_confidence > 0.0:
                    unavailable_confidence_rejections += 1
                    continue
            elif event_confidence.value < self._min_event_confidence:
                low_confidence_rejections += 1
                continue

            if cursor >= len(self._score_events):
                unmatched += 1
                continue

            observed_key = self._pitch_key(event.midi_pitches)
            search_stop = min(len(self._score_events), cursor + self._lookahead_events + 1)
            match_index = None
            for index in range(cursor, search_stop):
                if self._pitch_key(self._score_events[index].midi_pitches) == observed_key:
                    match_index = index
                    break

            if match_index is None:
                unmatched += 1
                continue

            skipped_score_events += match_index - cursor
            score_event = self._score_events[match_index]
            cursor = match_index + 1
            matched += 1
            updates.append(
                FollowerUpdate(
                    score_beat=score_event.score_beat,
                    emitted_at_s=event.observed_at_s,
                    backend=self.backend_name,
                    confidence=None if event_confidence is None else event_confidence.value,
                )
            )
            alignment_path.append(
                AlignmentPoint(
                    score_beat=score_event.score_beat,
                    performance_time_s=event.observed_at_s,
                )
            )

        return FollowerRunResult(
            backend=self.backend_name,
            backend_version=self.backend_version,
            method="forward_pitch_lookahead",
            input_type="symbolic",
            updates=tuple(updates),
            alignment_path=tuple(alignment_path),
            wall_duration_s=perf_counter() - started,
            backend_metrics={
                "matched_events": matched,
                "unmatched_observations": unmatched,
                "skipped_score_events": skipped_score_events,
                "low_confidence_rejections": low_confidence_rejections,
                "unavailable_confidence": unavailable_confidence,
                "unavailable_confidence_rejections": unavailable_confidence_rejections,
                "lookahead_events": self._lookahead_events,
                "min_event_confidence": self._min_event_confidence,
                "confidence_semantics": "propagated_when_available_otherwise_unavailable",
            },
        )
