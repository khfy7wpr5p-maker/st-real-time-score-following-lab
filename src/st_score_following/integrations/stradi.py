from __future__ import annotations

import csv
from math import isfinite
from pathlib import Path
from time import perf_counter

from st_score_following.contracts import PerformanceEventV1
from st_score_following.transcription import TranscriptionRunResult


class StradiCsvOutputAdapter:
    """Map STRAdi-style CSV output into ST note events without importing STRAdi."""

    backend_name = "stradi-external"

    def __init__(self, *, backend_version: str = "external", model_mode: str = "online") -> None:
        if not backend_version.strip():
            raise ValueError("backend_version must be non-empty")
        if model_mode not in {"online", "offline"}:
            raise ValueError("model_mode must be online or offline")
        self._backend_version = backend_version
        self._model_mode = model_mode

    @staticmethod
    def _parse_float(row: dict[str, str], field: str, row_number: int) -> float:
        try:
            value = float(row[field])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"invalid {field} at CSV row {row_number}") from exc
        if not isfinite(value):
            raise ValueError(f"non-finite {field} at CSV row {row_number}")
        return value

    @staticmethod
    def _parse_pitch(row: dict[str, str], row_number: int) -> int:
        try:
            pitch = int(row["midi_number"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"invalid midi_number at CSV row {row_number}") from exc
        if pitch < 0 or pitch > 127:
            raise ValueError(f"midi_number out of range at CSV row {row_number}")
        return pitch

    def load_csv(self, path: str | Path) -> TranscriptionRunResult:
        started = perf_counter()
        events: list[PerformanceEventV1] = []
        with Path(path).open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            required = {"onset", "offset", "midi_number"}
            if reader.fieldnames is None or not required.issubset(reader.fieldnames):
                raise ValueError("STRAdi CSV requires onset, offset and midi_number columns")

            for row_number, row in enumerate(reader, start=2):
                onset = self._parse_float(row, "onset", row_number)
                offset = self._parse_float(row, "offset", row_number)
                pitch = self._parse_pitch(row, row_number)
                if onset < 0 or offset < onset:
                    raise ValueError(f"invalid onset/offset order at CSV row {row_number}")
                events.append(
                    PerformanceEventV1(
                        event_id=f"stradi-{row_number - 1}",
                        observed_at_s=onset,
                        duration_s=offset - onset,
                        midi_pitches=(pitch,),
                        confidence=None,
                    )
                )

        return TranscriptionRunResult(
            backend=self.backend_name,
            backend_version=self._backend_version,
            events=tuple(events),
            wall_duration_s=perf_counter() - started,
            metadata={
                "model_mode": self._model_mode,
                "source_format": "stradi_csv_onset_offset_midi_number",
                "confidence_available": False,
                "timing_semantics": "csv_parse_time_not_model_inference_latency",
            },
        )
