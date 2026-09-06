from __future__ import annotations

import argparse
import json
import platform
import sys
import tempfile
from importlib import metadata
from pathlib import Path

from st_score_following.evaluation import (
    SYNTHETIC_NOTES,
    evaluate_expected_onsets,
    write_quarter_note_midi,
)
from st_score_following.followers import MatchmakerAdapter


def run() -> dict[str, object]:
    score = Path(__file__).parents[1] / "tests" / "fixtures" / "synthetic_piano.musicxml"

    with tempfile.TemporaryDirectory() as tmp:
        midi = Path(tmp) / "performance.mid"
        write_quarter_note_midi(midi)
        result = MatchmakerAdapter().run_files(
            score_file=str(score),
            performance_file=str(midi),
            input_type="midi",
            method="pthmm",
        )

    expected = tuple((float(i), i * 0.5) for i in range(len(SYNTHETIC_NOTES)))
    metrics = evaluate_expected_onsets(result.alignment_path, expected)
    performance_duration_s = len(SYNTHETIC_NOTES) * 0.5

    return {
        "schema": "st.score_following.benchmark.v1",
        "fixture": "synthetic_piano_quarter_notes_v1",
        "input_type": "midi",
        "method": result.method,
        "backend": result.backend,
        "backend_version": result.backend_version,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "pymatchmaker_distribution_version": metadata.version("pymatchmaker"),
        "updates": len(result.updates),
        "alignment_points": len(result.alignment_path),
        "confidence_available": result.confidence_available,
        "wall_duration_s": result.wall_duration_s,
        "backend_alignment_duration_s": result.backend_alignment_duration_s,
        "performance_duration_s": performance_duration_s,
        "realtime_factor": result.wall_duration_s / performance_duration_s,
        "metrics": metrics.to_dict(),
        "limitations": [
            "Synthetic monophonic piano-like MIDI; not a dataset-quality musical performance.",
            "Matchmaker high-level updates expose no calibrated confidence value.",
            (
                "This SF-01 baseline measures clean alignment only; "
                "recovery scenarios belong to SF-06."
            ),
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = run()
    rendered = json.dumps(report, indent=2, sort_keys=True, allow_nan=False)
    print(rendered)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
