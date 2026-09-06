from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite
from statistics import mean, median

from st_score_following.followers.base import AlignmentPoint


@dataclass(frozen=True, slots=True)
class AlignmentMetrics:
    evaluated_events: int
    failed_events: int
    median_absolute_error_ms: float
    mean_absolute_error_ms: float
    p95_absolute_error_ms: float
    within_50_ms: float
    within_100_ms: float
    within_250_ms: float
    within_500_ms: float
    failure_rate: float

    def to_dict(self) -> dict[str, int | float]:
        return asdict(self)


def _nearest_performance_time(
    path: tuple[AlignmentPoint, ...],
    score_beat: float,
) -> float | None:
    finite = [
        point
        for point in path
        if isfinite(point.score_beat) and isfinite(point.performance_time_s)
    ]
    if not finite:
        return None
    nearest = min(finite, key=lambda point: abs(point.score_beat - score_beat))
    return nearest.performance_time_s


def _percentile_95(values: list[float]) -> float:
    if not values:
        return float("nan")
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, int(0.95 * len(ordered) + 0.999999) - 1))
    return ordered[index]


def evaluate_expected_onsets(
    path: tuple[AlignmentPoint, ...],
    expected: tuple[tuple[float, float], ...],
) -> AlignmentMetrics:
    errors_ms: list[float] = []
    failures = 0

    for score_beat, expected_time_s in expected:
        predicted = _nearest_performance_time(path, score_beat)
        if predicted is None:
            failures += 1
            continue
        errors_ms.append(abs(predicted - expected_time_s) * 1000.0)

    total = len(expected)
    evaluated = len(errors_ms)
    denominator = evaluated or 1

    def within(threshold_ms: float) -> float:
        return sum(error <= threshold_ms for error in errors_ms) / denominator

    return AlignmentMetrics(
        evaluated_events=evaluated,
        failed_events=failures,
        median_absolute_error_ms=median(errors_ms) if errors_ms else float("nan"),
        mean_absolute_error_ms=mean(errors_ms) if errors_ms else float("nan"),
        p95_absolute_error_ms=_percentile_95(errors_ms),
        within_50_ms=within(50.0),
        within_100_ms=within(100.0),
        within_250_ms=within(250.0),
        within_500_ms=within(500.0),
        failure_rate=(failures / total) if total else 0.0,
    )
