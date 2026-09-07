from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass
from math import isfinite
from time import perf_counter

from .contracts import PerformanceEventV1
from .followers.base import AlignmentPoint, FollowerRunResult, FollowerUpdate
from .symbolic import SymbolicScoreEvent


@dataclass(frozen=True, slots=True)
class RecoveryMatch:
    event_id: str
    score_index: int
    score_beat: float
    observed_at_s: float
    similarity: float
    transition: str
    search_scope: str
    gap_s: float | None
    confidence: float | None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class RecoveryAwareSymbolicFollower:
    """Causal symbolic follower with explicit bounded and global re-lock behavior."""

    backend_name = "st-symbolic-recovery"
    backend_version = "0.1.0"

    def __init__(
        self,
        score_events: Iterable[SymbolicScoreEvent],
        *,
        forward_window: int = 8,
        backward_window: int = 8,
        min_pitch_similarity: float = 1.0,
        pause_gap_s: float = 1.5,
        global_search_after_mismatches: int = 2,
        min_event_confidence: float = 0.0,
    ) -> None:
        self._score_events = tuple(score_events)
        if not self._score_events:
            raise ValueError("score_events must not be empty")
        if forward_window < 0 or backward_window < 0:
            raise ValueError("search windows must be >= 0")
        if not 0.0 <= min_pitch_similarity <= 1.0:
            raise ValueError("min_pitch_similarity must be within [0, 1]")
        if not isfinite(pause_gap_s) or pause_gap_s <= 0:
            raise ValueError("pause_gap_s must be finite and > 0")
        if global_search_after_mismatches < 1:
            raise ValueError("global_search_after_mismatches must be >= 1")
        if not 0.0 <= min_event_confidence <= 1.0:
            raise ValueError("min_event_confidence must be within [0, 1]")
        self._forward_window = forward_window
        self._backward_window = backward_window
        self._min_pitch_similarity = min_pitch_similarity
        self._pause_gap_s = pause_gap_s
        self._global_search_after_mismatches = global_search_after_mismatches
        self._min_event_confidence = min_event_confidence

    @staticmethod
    def _pitch_set(pitches: tuple[int, ...]) -> frozenset[int]:
        return frozenset(pitches)

    def _similarity(self, observed: frozenset[int], score_index: int) -> float:
        expected = self._pitch_set(self._score_events[score_index].midi_pitches)
        union = observed | expected
        if not union:
            return 0.0
        return len(observed & expected) / len(union)

    def _best_candidate(
        self,
        indices: range,
        observed: frozenset[int],
        expected_index: int,
    ) -> tuple[int, float] | None:
        candidates: list[tuple[float, int, int]] = []
        for index in indices:
            similarity = self._similarity(observed, index)
            if similarity < self._min_pitch_similarity:
                continue
            candidates.append((similarity, -abs(index - expected_index), index))
        if not candidates:
            return None
        similarity, _, index = max(candidates)
        return index, similarity

    def run_events(self, events: Iterable[PerformanceEventV1]) -> FollowerRunResult:
        started = perf_counter()
        last_score_index: int | None = None
        previous_observed_at_s: float | None = None
        mismatch_streak = 0
        unmatched = 0
        low_confidence_rejections = 0
        unavailable_confidence = 0
        unavailable_confidence_rejections = 0
        pause_gaps = 0
        forward_skipped_events = 0
        backward_jumps = 0
        restart_relocks = 0
        global_relocks = 0
        updates: list[FollowerUpdate] = []
        alignment_path: list[AlignmentPoint] = []
        matches: list[RecoveryMatch] = []

        for event in events:
            if previous_observed_at_s is not None and event.observed_at_s < previous_observed_at_s:
                raise ValueError("events must be ordered by non-decreasing observed_at_s")
            gap_s = (
                None
                if previous_observed_at_s is None
                else event.observed_at_s - previous_observed_at_s
            )
            previous_observed_at_s = event.observed_at_s
            if gap_s is not None and gap_s >= self._pause_gap_s:
                pause_gaps += 1

            if event.confidence is None:
                unavailable_confidence += 1
                if self._min_event_confidence > 0:
                    unavailable_confidence_rejections += 1
                    continue
            elif event.confidence.value < self._min_event_confidence:
                low_confidence_rejections += 1
                continue

            observed = self._pitch_set(event.midi_pitches)
            if not observed:
                unmatched += 1
                mismatch_streak += 1
                continue

            if last_score_index is None:
                expected_index = 0
            else:
                expected_index = min(last_score_index + 1, len(self._score_events) - 1)

            local_start = max(0, expected_index - self._backward_window)
            local_stop = min(
                len(self._score_events),
                expected_index + self._forward_window + 1,
            )
            candidate = self._best_candidate(
                range(local_start, local_stop),
                observed,
                expected_index,
            )
            search_scope = "local"

            allow_global = (
                last_score_index is None
                or (gap_s is not None and gap_s >= self._pause_gap_s)
                or mismatch_streak + 1 >= self._global_search_after_mismatches
            )
            if candidate is None and allow_global:
                candidate = self._best_candidate(
                    range(len(self._score_events)),
                    observed,
                    expected_index,
                )
                if last_score_index is None:
                    search_scope = "global_initial"
                elif gap_s is not None and gap_s >= self._pause_gap_s:
                    search_scope = "global_gap"
                else:
                    search_scope = "global_after_mismatch"

            if candidate is None:
                unmatched += 1
                mismatch_streak += 1
                continue

            score_index, similarity = candidate
            if last_score_index is None:
                transition = "initial"
            else:
                expected_after_last = last_score_index + 1
                if score_index == expected_after_last:
                    transition = "advance"
                elif score_index > expected_after_last:
                    transition = "forward_skip"
                    forward_skipped_events += score_index - expected_after_last
                elif score_index == last_score_index:
                    transition = "repeat_same"
                elif score_index == 0 and gap_s is not None and gap_s >= self._pause_gap_s:
                    transition = "restart"
                    restart_relocks += 1
                else:
                    transition = "backward_jump"
                    backward_jumps += 1

            if search_scope.startswith("global") and last_score_index is not None:
                global_relocks += 1

            score_event = self._score_events[score_index]
            confidence = None if event.confidence is None else event.confidence.value
            matches.append(
                RecoveryMatch(
                    event_id=event.event_id,
                    score_index=score_index,
                    score_beat=score_event.score_beat,
                    observed_at_s=event.observed_at_s,
                    similarity=similarity,
                    transition=transition,
                    search_scope=search_scope,
                    gap_s=gap_s,
                    confidence=confidence,
                )
            )
            updates.append(
                FollowerUpdate(
                    score_beat=score_event.score_beat,
                    emitted_at_s=event.observed_at_s,
                    backend=self.backend_name,
                    confidence=confidence,
                )
            )
            alignment_path.append(
                AlignmentPoint(
                    score_beat=score_event.score_beat,
                    performance_time_s=event.observed_at_s,
                )
            )
            last_score_index = score_index
            mismatch_streak = 0

        return FollowerRunResult(
            backend=self.backend_name,
            backend_version=self.backend_version,
            method="bounded_bidirectional_pitch_recovery",
            input_type="symbolic",
            updates=tuple(updates),
            alignment_path=tuple(alignment_path),
            wall_duration_s=perf_counter() - started,
            backend_metrics={
                "matches": [match.to_dict() for match in matches],
                "matched_events": len(matches),
                "unmatched_observations": unmatched,
                "low_confidence_rejections": low_confidence_rejections,
                "unavailable_confidence": unavailable_confidence,
                "unavailable_confidence_rejections": unavailable_confidence_rejections,
                "pause_gaps": pause_gaps,
                "forward_skipped_score_events": forward_skipped_events,
                "backward_jumps": backward_jumps,
                "restart_relocks": restart_relocks,
                "global_relocks": global_relocks,
                "forward_window": self._forward_window,
                "backward_window": self._backward_window,
                "min_pitch_similarity": self._min_pitch_similarity,
                "pause_gap_s": self._pause_gap_s,
                "global_search_after_mismatches": self._global_search_after_mismatches,
                "confidence_semantics": "propagated_when_available_otherwise_unavailable",
            },
        )
