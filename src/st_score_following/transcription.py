from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from .contracts import PerformanceEventV1


@dataclass(frozen=True, slots=True)
class TranscriptionRunResult:
    """Backend-neutral note-event output from a transcription backend."""

    backend: str
    backend_version: str
    events: tuple[PerformanceEventV1, ...]
    wall_duration_s: float
    metadata: dict[str, object] = field(default_factory=dict)


class TranscriptionAdapter(Protocol):
    """Boundary for future audio-to-note transcription backends."""

    def transcribe(
        self,
        *,
        samples: object,
        sample_rate: int,
    ) -> TranscriptionRunResult: ...
