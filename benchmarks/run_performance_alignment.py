from __future__ import annotations

import json

from st_score_following import AlignmentProvenanceV1, build_performance_alignment_report
from st_score_following.followers.base import AlignmentPoint


def _path(beats: tuple[float, ...], times: tuple[float, ...]) -> tuple[AlignmentPoint, ...]:
    return tuple(
        AlignmentPoint(score_beat=beat, performance_time_s=time)
        for beat, time in zip(beats, times, strict=True)
    )


def _run_case(
    name: str,
    beats: tuple[float, ...],
    times: tuple[float, ...],
) -> dict[str, object]:
    report = build_performance_alignment_report(
        _path(beats, times),
        reference_bpm=120.0,
        provenance=AlignmentProvenanceV1(
            backend="st-sf07-synthetic",
            backend_version="0.1.0",
            method=name,
            input_type="alignment_path",
            run_id="sf07-repository-owned",
        ),
        on_time_tolerance_ms=40.0,
        pause_gap_s=1.5,
    )
    return {
        "summary": report.summary.to_dict(),
        "segments": [point.segment_id for point in report.points],
        "boundary_reasons": [
            None if point.boundary_reason is None else point.boundary_reason.value
            for point in report.points
        ],
        "local_tempos_bpm": [
            point.local_tempo_bpm for point in report.points if point.local_tempo_bpm is not None
        ],
        "json_bytes": len(report.to_json().encode("utf-8")),
        "csv_lines": len(report.to_csv().splitlines()),
    }


def run() -> dict[str, object]:
    return {
        "schema": "st.score_following.performance_alignment_benchmark.v1",
        "reference_bpm": 120.0,
        "on_time_tolerance_ms": 40.0,
        "cases": {
            "clean": _run_case(
                "clean",
                tuple(float(i) for i in range(8)),
                tuple(i * 0.5 for i in range(8)),
            ),
            "expressive": _run_case(
                "expressive",
                (0.0, 1.0, 2.0, 3.0, 4.0, 5.0),
                (0.0, 0.45, 1.06, 1.48, 2.09, 2.50),
            ),
            "pause": _run_case(
                "pause",
                (0.0, 1.0, 2.0, 3.0, 4.0),
                (0.0, 0.5, 1.0, 3.5, 4.0),
            ),
            "backward_jump": _run_case(
                "backward_jump",
                (0.0, 1.0, 2.0, 1.0, 2.0, 3.0),
                (0.0, 0.5, 1.0, 1.5, 2.0, 2.5),
            ),
        },
        "boundaries": [
            "segment deviation is anchored independently at each segment start",
            "pause gaps and non-forward score movement start new segments",
            "local tempo is never computed across a segment boundary",
            "missing confidence remains null/blank in JSON/CSV exports",
            "score_time assumes score_beat uses the reference BPM beat unit",
        ],
    }


def main() -> None:
    print(json.dumps(run(), indent=2, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
