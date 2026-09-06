from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from math import isfinite
from typing import Any


class ObservationKind(StrEnum):
    AUDIO_FEATURE = "audio_feature"
    MIDI_EVENT = "midi_event"
    SYMBOLIC_EVENT = "symbolic_event"


def _finite_non_negative(name: str, value: float) -> None:
    if not isfinite(value) or value < 0:
        raise ValueError(f"{name} must be finite and >= 0")


@dataclass(frozen=True, slots=True)
class ConfidenceV1:
    value: float
    source: str
    calibrated: bool = False
    reason: str | None = None
    schema_version: str = field(default="confidence_v1", init=False)

    def __post_init__(self) -> None:
        if not isfinite(self.value) or not 0.0 <= self.value <= 1.0:
            raise ValueError("confidence value must be finite and within [0, 1]")
        if not self.source.strip():
            raise ValueError("confidence source must be non-empty")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ScorePositionV1:
    measure_index: int
    beat: float
    score_time_s: float | None = None
    part_id: str | None = None
    semantic_address: str | None = None
    schema_version: str = field(default="score_position_v1", init=False)

    def __post_init__(self) -> None:
        if self.measure_index < 0:
            raise ValueError("measure_index must be >= 0")
        _finite_non_negative("beat", self.beat)
        if self.score_time_s is not None:
            _finite_non_negative("score_time_s", self.score_time_s)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class TempoStateV1:
    bpm: float
    beat_phase: float
    observed_at_s: float
    confidence: ConfidenceV1
    schema_version: str = field(default="tempo_state_v1", init=False)

    def __post_init__(self) -> None:
        if not isfinite(self.bpm) or self.bpm <= 0:
            raise ValueError("bpm must be finite and > 0")
        if not isfinite(self.beat_phase) or not 0.0 <= self.beat_phase < 1.0:
            raise ValueError("beat_phase must be finite and within [0, 1)")
        _finite_non_negative("observed_at_s", self.observed_at_s)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ObservationV1:
    observation_id: str
    sequence_id: int
    observed_at_s: float
    kind: ObservationKind
    payload: Mapping[str, Any]
    schema_version: str = field(default="observation_v1", init=False)

    def __post_init__(self) -> None:
        if not self.observation_id.strip():
            raise ValueError("observation_id must be non-empty")
        if self.sequence_id < 0:
            raise ValueError("sequence_id must be >= 0")
        _finite_non_negative("observed_at_s", self.observed_at_s)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["kind"] = self.kind.value
        return data


@dataclass(frozen=True, slots=True)
class AlignmentV1:
    score_event_id: str
    observation_id: str
    score_time_s: float
    performance_time_s: float
    confidence: ConfidenceV1
    schema_version: str = field(default="alignment_v1", init=False)

    def __post_init__(self) -> None:
        if not self.score_event_id.strip() or not self.observation_id.strip():
            raise ValueError("event identifiers must be non-empty")
        _finite_non_negative("score_time_s", self.score_time_s)
        _finite_non_negative("performance_time_s", self.performance_time_s)

    @property
    def deviation_s(self) -> float:
        return self.performance_time_s - self.score_time_s

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["deviation_s"] = self.deviation_s
        return data


@dataclass(frozen=True, slots=True)
class PerformanceEventV1:
    event_id: str
    observed_at_s: float
    duration_s: float | None
    midi_pitches: tuple[int, ...]
    confidence: ConfidenceV1
    schema_version: str = field(default="performance_event_v1", init=False)

    def __post_init__(self) -> None:
        if not self.event_id.strip():
            raise ValueError("event_id must be non-empty")
        _finite_non_negative("observed_at_s", self.observed_at_s)
        if self.duration_s is not None:
            _finite_non_negative("duration_s", self.duration_s)
        if any(pitch < 0 or pitch > 127 for pitch in self.midi_pitches):
            raise ValueError("midi pitches must be within [0, 127]")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
