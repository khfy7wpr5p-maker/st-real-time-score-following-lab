from __future__ import annotations

from collections.abc import Callable
from importlib import import_module, metadata
from math import isfinite
from time import perf_counter
from typing import Any

from .base import AlignmentPoint, FollowerRunResult, FollowerUpdate

MATCHMAKER_DISTRIBUTION = "pymatchmaker"
SUPPORTED_MATCHMAKER_VERSION = "0.3.0"


def _normalize_alignment_path(path: Any) -> tuple[AlignmentPoint, ...]:
    if path is None:
        return ()

    try:
        if len(path) != 2:
            raise ValueError("Matchmaker alignment path must have shape (2, T)")
        score_axis, performance_axis = path[0], path[1]
        if len(score_axis) != len(performance_axis):
            raise ValueError("Matchmaker alignment axes must have equal length")
    except TypeError as exc:
        raise ValueError("Matchmaker alignment path is not indexable") from exc

    points: list[AlignmentPoint] = []
    for score_beat, performance_time_s in zip(score_axis, performance_axis, strict=True):
        score = float(score_beat)
        perf = float(performance_time_s)
        if not isfinite(score) or not isfinite(perf):
            continue
        points.append(AlignmentPoint(score_beat=score, performance_time_s=perf))
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
            factory = getattr(module, "Matchmaker")
            backend_version = metadata.version(MATCHMAKER_DISTRIBUTION)

        self._factory = factory
        self.backend_version = backend_version or "unknown"
        if strict_version and self.backend_version != self.supported_version:
            raise RuntimeError(
                "Unsupported pymatchmaker version "
                f"{self.backend_version!r}; expected {self.supported_version!r}"
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
        generator = backend.run(verbose=verbose)

        started = perf_counter()
        updates: list[FollowerUpdate] = []
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
            updates.append(
                FollowerUpdate(
                    score_beat=score_beat,
                    emitted_at_s=perf_counter() - started,
                    backend=self.backend_name,
                    confidence=None,
                )
            )

        wall_duration_s = perf_counter() - started
        backend_duration = getattr(backend, "alignment_duration", None)
        if backend_duration is not None:
            backend_duration = float(backend_duration)

        resolved_method = method or getattr(backend, "method", "default")
        return FollowerRunResult(
            backend=self.backend_name,
            backend_version=self.backend_version,
            method=str(resolved_method),
            input_type=input_type,
            updates=tuple(updates),
            alignment_path=_normalize_alignment_path(alignment_path),
            wall_duration_s=wall_duration_s,
            backend_alignment_duration_s=backend_duration,
        )
