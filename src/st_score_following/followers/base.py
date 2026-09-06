from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class AlignmentPoint:
    """Backend-neutral score-beat/performance-time alignment point."""

    score_beat: float
    performance_time_s: float


@dataclass(frozen=True, slots=True)
class FollowerUpdate:
    """One online follower update before score-timeline semantic addressing."""

    score_beat: float
    emitted_at_s: float
    backend: str
    confidence: float | None = None


@dataclass(frozen=True, slots=True)
class FollowerRunResult:
    """Collected result for a finite offline/streamed follower run."""

    backend: str
    backend_version: str
    method: str
    input_type: str
    updates: tuple[FollowerUpdate, ...]
    alignment_path: tuple[AlignmentPoint, ...]
    wall_duration_s: float
    backend_alignment_duration_s: float | None = None
    backend_metrics: dict[str, Any] = field(default_factory=dict)

    @property
    def confidence_available(self) -> bool:
        return any(update.confidence is not None for update in self.updates)


class FollowerAdapter(Protocol):
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
    ) -> FollowerRunResult: ...
