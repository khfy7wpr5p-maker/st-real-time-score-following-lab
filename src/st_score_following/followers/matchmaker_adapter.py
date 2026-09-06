from __future__ import annotations

from collections.abc import Callable
from importlib import import_module, metadata
from math import isfinite
from time import perf_counter
from typing import Any

from st_score_following.clock import summarize_latency_s

from .base import AlignmentPoint, FollowerRunResult, FollowerUpdate

MATCHMAKER_DISTRIBUTION = "pymatchmaker"
SUPPORTED_MATCHMAKER_VERSION = "0.3.0"


def _finite_point(score_beat: Any, performance_time_s: Any) -> AlignmentPoint | None:
    score = float(score_beat)
    perf = float(performance_time_s)
    if not isfinite(score) or not isfinite(perf):
        return None
    return AlignmentPoint(score_beat=score, performance_time_s=perf)


def _normalize_alignment_path(path: Any) -> tuple[AlignmentPoint, ...]:
    """Normalize Matchmaker's documented ndarray and observed list-of-pairs forms."""
    if path is None:
        return ()

    try:
        shape = path.shape
    except AttributeError:
        shape = None

    points: list[AlignmentPoint] = []
    if shape is not None and len(shape) == 2 and shape[0] == 2:
        score_axis, performance_axis = path[0], path[1]
        if len(score_axis) != len(performance_axis):
            raise ValueError("Matchmaker alignment axes must have equal length")
        for score_beat, performance_time_s in zip(
            score_axis,
            performance_axis,
            strict=True,
        ):
            point = _finite_point(score_beat, performance_time_s)
            if point is not None:
                points.append(point)
        return tuple(points)

    try:
        for item in path:
            if len(item) != 2:
                raise ValueError("Matchmaker pair alignment entries must have length 2")
            point = _finite_point(item[0], item[1])
            if point is not None:
                points.append(point)
    except TypeError as exc:
        raise ValueError("Matchmaker alignment path is not a supported sequence") from exc

    return tuple(points)


class MatchmakerAdapter:
    """Version-pinned adapter around pymatchmaker's high-level Matchmaker API."""

    backend_name = "matchmaker"
    supported_version = SUPPORTED_MATCHMAKER_VERSION

    def __init__(
        self,
        *,
        factory: Callable[..., Any] | None = None,
        backend_version: str | None = None,
        strict_version: bool = True,
    ) -> None:
        if factory is None:
            module = import_module("matchmaker")
            factory = module.Matchmaker
            backend_version = metadata.version(MATCHMAKER_DISTRIBUTION)

        self._factory = factory
        self.backend_version = backend_version or "unknown"
        if strict_version and self.backend_version != self.supported_version:
            raise RuntimeError(
                "Unsupported pymatchmaker version "
                f"{self.backend_version!r}; expected {self.supported_version!r}"
            )

    def _collect_run(
        self,
        *,
        backend: Any,
        input_type: str,
        method: str | None,
        verbose: bool,
        emitted_clock: Callable[[], float] | None = None,
        source_arrival_clock: Callable[[], float | None] | None = None,
    ) -> FollowerRunResult:
        generator = backend.run(verbose=verbose)
        started = perf_counter()
        emission_clock = emitted_clock or (lambda: perf_counter() - started)
        updates: list[FollowerUpdate] = []
        pipeline_latencies_s: list[float] = []
        alignment_path = None

        while True:
            try:
                position = next(generator)
            except StopIteration as stop:
                alignment_path = stop.value
                break

            score_beat = float(position)
            if not isfinite(score_beat):
                continue

            emitted_at_s = emission_clock()
            if source_arrival_clock is not None:
                source_arrival_s = source_arrival_clock()
                if source_arrival_s is not None and emitted_at_s >= source_arrival_s:
                    pipeline_latencies_s.append(emitted_at_s - source_arrival_s)

            updates.append(
                FollowerUpdate(
                    score_beat=score_beat,
                    emitted_at_s=emitted_at_s,
                    backend=self.backend_name,
                    confidence=None,
                )
            )

        wall_duration_s = perf_counter() - started
        backend_duration = backend.alignment_duration
        if backend_duration is not None:
            backend_duration = float(backend_duration)

        backend_metrics: dict[str, Any] = {}
        if pipeline_latencies_s:
            latency = summarize_latency_s(pipeline_latencies_s)
            backend_metrics["pipeline_latency"] = {
                "boundary": "st_ingress_accept_to_follower_update",
                "samples": latency.count,
                "mean_s": latency.mean_s,
                "p95_s": latency.p95_s,
                "max_s": latency.max_s,
            }

        resolved_method = method or backend.method
        return FollowerRunResult(
            backend=self.backend_name,
            backend_version=self.backend_version,
            method=str(resolved_method),
            input_type=input_type,
            updates=tuple(updates),
            alignment_path=_normalize_alignment_path(alignment_path),
            wall_duration_s=wall_duration_s,
            backend_alignment_duration_s=backend_duration,
            backend_metrics=backend_metrics,
        )

    def run_files(
        self,
        *,
        score_file: str,
        performance_file: str,
        input_type: str,
        method: str | None = None,
        wait: bool = False,
        verbose: bool = False,
        kwargs: dict[str, Any] | None = None,
    ) -> FollowerRunResult:
        backend = self._factory(
            score_file=score_file,
            performance_file=performance_file,
            input_type=input_type,
            method=method,
            wait=wait,
            kwargs=kwargs,
        )
        return self._collect_run(
            backend=backend,
            input_type=input_type,
            method=method,
            verbose=verbose,
        )

    def run_stream(
        self,
        *,
        score_file: str,
        stream: Any,
        input_type: str,
        method: str | None = None,
        verbose: bool = False,
        kwargs: dict[str, Any] | None = None,
        emitted_clock: Callable[[], float] | None = None,
        source_arrival_clock: Callable[[], float | None] | None = None,
    ) -> FollowerRunResult:
        backend = self._factory(
            score_file=score_file,
            performance_file=None,
            input_type=input_type,
            method=method,
            stream=stream,
            wait=False,
            kwargs=kwargs,
        )
        return self._collect_run(
            backend=backend,
            input_type=input_type,
            method=method,
            verbose=verbose,
            emitted_clock=emitted_clock,
            source_arrival_clock=source_arrival_clock,
        )
