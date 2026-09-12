from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from math import isfinite
from statistics import median
from time import perf_counter

from .contracts import ConfidenceV1


def _canonical_pitch_classes(values: tuple[int, ...]) -> tuple[int, ...]:
    if not values:
        raise ValueError("texture_pitch_classes must not be empty")
    if any(value < 0 or value > 11 for value in values):
        raise ValueError("texture pitch classes must be within [0, 11]")
    canonical = tuple(sorted(set(values)))
    if canonical != values:
        raise ValueError("texture_pitch_classes must be sorted and unique")
    return canonical


def _percentile(values: list[float], fraction: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, int((len(ordered) - 1) * fraction + 0.5))
    return ordered[index]


@dataclass(frozen=True, slots=True)
class OrchestraGlobalScorePointV1:
    score_index: int
    measure_index: int
    beat_in_measure: float
    score_beat: float
    texture_pitch_classes: tuple[int, ...]
    schema_version: str = field(default="orchestra_global_score_point_v1", init=False)

    def __post_init__(self) -> None:
        if self.score_index < 0:
            raise ValueError("score_index must be >= 0")
        if self.measure_index < 1:
            raise ValueError("measure_index must be >= 1")
        if not isfinite(self.beat_in_measure) or self.beat_in_measure < 1:
            raise ValueError("beat_in_measure must be finite and >= 1")
        if not isfinite(self.score_beat) or self.score_beat < 0:
            raise ValueError("score_beat must be finite and >= 0")
        _canonical_pitch_classes(self.texture_pitch_classes)


@dataclass(frozen=True, slots=True)
class OrchestraGlobalObservationV1:
    event_id: str
    observed_at_s: float
    texture_pitch_classes: tuple[int, ...]
    confidence: ConfidenceV1 | None = None
    schema_version: str = field(default="orchestra_global_observation_v1", init=False)

    def __post_init__(self) -> None:
        if not self.event_id.strip():
            raise ValueError("event_id must be non-empty")
        if not isfinite(self.observed_at_s) or self.observed_at_s < 0:
            raise ValueError("observed_at_s must be finite and >= 0")
        _canonical_pitch_classes(self.texture_pitch_classes)


@dataclass(frozen=True, slots=True)
class OrchestraGlobalMatchV1:
    event_id: str
    score_index: int
    measure_index: int
    beat_in_measure: float
    score_beat: float
    observed_at_s: float
    texture_similarity: float
    transition: str
    search_scope: str
    gap_s: float | None
    processing_latency_ms: float
    confidence: float | None
    schema_version: str = field(default="orchestra_global_match_v1", init=False)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class OrchestraGlobalSummaryV1:
    score_point_count: int
    observation_count: int
    matched_observations: int
    unmatched_observations: int
    low_confidence_rejections: int
    unavailable_confidence_observations: int
    unavailable_confidence_rejections: int
    pause_gaps: int
    forward_skipped_score_points: int
    backward_jumps: int
    restart_relocks: int
    global_relocks: int
    median_processing_latency_ms: float
    p95_processing_latency_ms: float
    max_processing_latency_ms: float
    confidence_available_matches: int
    schema_version: str = field(default="orchestra_global_summary_v1", init=False)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class OrchestraGlobalReportV1:
    matches: tuple[OrchestraGlobalMatchV1, ...]
    summary: OrchestraGlobalSummaryV1
    authority_boundary: str = field(
        default="global_measure_beat_research_not_per_instrument_transcription_authority",
        init=False,
    )
    schema_version: str = field(default="orchestra_global_report_v1", init=False)

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "authority_boundary": self.authority_boundary,
            "summary": self.summary.to_dict(),
            "matches": [match.to_dict() for match in self.matches],
        }


class OrchestraGlobalFollower:
    """Global measure/beat follower over aggregate orchestral texture fingerprints."""

    def __init__(
        self,
        score_points: Iterable[OrchestraGlobalScorePointV1],
        *,
        forward_window: int = 6,
        backward_window: int = 10,
        min_texture_similarity: float = 0.45,
        pause_gap_s: float = 1.5,
        global_search_after_mismatches: int = 2,
        min_observation_confidence: float = 0.0,
    ) -> None:
        self._score_points = tuple(score_points)
        if not self._score_points:
            raise ValueError("score_points must not be empty")
        if tuple(point.score_index for point in self._score_points) != tuple(
            range(len(self._score_points))
        ):
            raise ValueError("score_index values must be contiguous from zero")
        if any(
            current.score_beat < previous.score_beat
            for previous, current in zip(self._score_points, self._score_points[1:], strict=False)
        ):
            raise ValueError("score_points must be ordered by non-decreasing score_beat")
        if forward_window < 0 or backward_window < 0:
            raise ValueError("search windows must be >= 0")
        if not 0 <= min_texture_similarity <= 1:
            raise ValueError("min_texture_similarity must be within [0, 1]")
        if not isfinite(pause_gap_s) or pause_gap_s <= 0:
            raise ValueError("pause_gap_s must be finite and > 0")
        if global_search_after_mismatches < 1:
            raise ValueError("global_search_after_mismatches must be >= 1")
        if not 0 <= min_observation_confidence <= 1:
            raise ValueError("min_observation_confidence must be within [0, 1]")
        self._forward_window = forward_window
        self._backward_window = backward_window
        self._min_texture_similarity = min_texture_similarity
        self._pause_gap_s = pause_gap_s
        self._global_search_after_mismatches = global_search_after_mismatches
        self._min_observation_confidence = min_observation_confidence

    @staticmethod
    def _similarity(observed: tuple[int, ...], expected: tuple[int, ...]) -> float:
        observed_set = frozenset(observed)
        expected_set = frozenset(expected)
        union = observed_set | expected_set
        return len(observed_set & expected_set) / len(union)

    def _best_candidate(
        self,
        indices: range,
        observed: tuple[int, ...],
        expected_index: int,
    ) -> tuple[int, float] | None:
        candidates: list[tuple[float, int, int]] = []
        for index in indices:
            similarity = self._similarity(
                observed,
                self._score_points[index].texture_pitch_classes,
            )
            if similarity < self._min_texture_similarity:
                continue
            candidates.append((similarity, -abs(index - expected_index), index))
        if not candidates:
            return None
        similarity, _, index = max(candidates)
        return index, similarity

    def run(self, observations: Iterable[OrchestraGlobalObservationV1]) -> OrchestraGlobalReportV1:
        last_score_index: int | None = None
        previous_observed_at_s: float | None = None
        mismatch_streak = 0
        unmatched = 0
        low_confidence_rejections = 0
        unavailable_confidence = 0
        unavailable_confidence_rejections = 0
        pause_gaps = 0
        forward_skips = 0
        backward_jumps = 0
        restart_relocks = 0
        global_relocks = 0
        processing_latencies_ms: list[float] = []
        matches: list[OrchestraGlobalMatchV1] = []

        observation_count = 0
        for observation in observations:
            observation_count += 1
            started = perf_counter()
            if (
                previous_observed_at_s is not None
                and observation.observed_at_s < previous_observed_at_s
            ):
                raise ValueError("observations must be ordered by observed_at_s")
            gap_s = (
                None
                if previous_observed_at_s is None
                else observation.observed_at_s - previous_observed_at_s
            )
            previous_observed_at_s = observation.observed_at_s
            if gap_s is not None and gap_s >= self._pause_gap_s:
                pause_gaps += 1

            if observation.confidence is None:
                unavailable_confidence += 1
                if self._min_observation_confidence > 0:
                    unavailable_confidence_rejections += 1
                    processing_latencies_ms.append((perf_counter() - started) * 1000)
                    continue
            elif observation.confidence.value < self._min_observation_confidence:
                low_confidence_rejections += 1
                processing_latencies_ms.append((perf_counter() - started) * 1000)
                continue

            expected_index = (
                0
                if last_score_index is None
                else min(last_score_index + 1, len(self._score_points) - 1)
            )
            local_start = max(0, expected_index - self._backward_window)
            local_stop = min(
                len(self._score_points),
                expected_index + self._forward_window + 1,
            )
            force_global = last_score_index is None or (
                gap_s is not None and gap_s >= self._pause_gap_s
            )
            if force_global:
                candidate = self._best_candidate(
                    range(len(self._score_points)),
                    observation.texture_pitch_classes,
                    expected_index,
                )
                search_scope = "global_initial" if last_score_index is None else "global_gap"
            else:
                candidate = self._best_candidate(
                    range(local_start, local_stop),
                    observation.texture_pitch_classes,
                    expected_index,
                )
                search_scope = "local"
                if (
                    candidate is None
                    and mismatch_streak + 1 >= self._global_search_after_mismatches
                ):
                    candidate = self._best_candidate(
                        range(len(self._score_points)),
                        observation.texture_pitch_classes,
                        expected_index,
                    )
                    search_scope = "global_after_mismatch"

            if candidate is None:
                unmatched += 1
                mismatch_streak += 1
                processing_latencies_ms.append((perf_counter() - started) * 1000)
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
                    forward_skips += score_index - expected_after_last
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

            processing_latency_ms = (perf_counter() - started) * 1000
            processing_latencies_ms.append(processing_latency_ms)
            score_point = self._score_points[score_index]
            confidence = None if observation.confidence is None else observation.confidence.value
            matches.append(
                OrchestraGlobalMatchV1(
                    event_id=observation.event_id,
                    score_index=score_index,
                    measure_index=score_point.measure_index,
                    beat_in_measure=score_point.beat_in_measure,
                    score_beat=score_point.score_beat,
                    observed_at_s=observation.observed_at_s,
                    texture_similarity=similarity,
                    transition=transition,
                    search_scope=search_scope,
                    gap_s=gap_s,
                    processing_latency_ms=processing_latency_ms,
                    confidence=confidence,
                )
            )
            last_score_index = score_index
            mismatch_streak = 0

        summary = OrchestraGlobalSummaryV1(
            score_point_count=len(self._score_points),
            observation_count=observation_count,
            matched_observations=len(matches),
            unmatched_observations=unmatched,
            low_confidence_rejections=low_confidence_rejections,
            unavailable_confidence_observations=unavailable_confidence,
            unavailable_confidence_rejections=unavailable_confidence_rejections,
            pause_gaps=pause_gaps,
            forward_skipped_score_points=forward_skips,
            backward_jumps=backward_jumps,
            restart_relocks=restart_relocks,
            global_relocks=global_relocks,
            median_processing_latency_ms=median(processing_latencies_ms)
            if processing_latencies_ms
            else 0.0,
            p95_processing_latency_ms=_percentile(processing_latencies_ms, 0.95),
            max_processing_latency_ms=max(processing_latencies_ms, default=0.0),
            confidence_available_matches=sum(match.confidence is not None for match in matches),
        )
        return OrchestraGlobalReportV1(matches=tuple(matches), summary=summary)
